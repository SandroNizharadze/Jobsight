# CVAccess Database Issue Fix

## Problem
The CV database was throwing a 500 error in production due to `MultipleObjectsReturned` exception when accessing `/employer/cv-database/`. The error occurred because:

1. The `CVAccess` model had no unique constraint on the combination of `employer_profile` and `candidate_profile`
2. This allowed duplicate records to be created for the same employer-candidate pair
3. When `get_or_create()` was called, it found multiple records and threw an exception

## Root Cause
```python
# In core/repositories/employer_repository.py line 77
cv_access, created = CVAccess.objects.get_or_create(
    employer_profile=employer_profile,
    candidate_profile=candidate_profile
)
```

This code expected only one record per employer-candidate pair, but the database contained multiple records.

## Solution

### 1. Added Unique Constraint
Added `unique_together` constraint to the `CVAccess` model:

```python
class CVAccess(models.Model):
    employer_profile = models.ForeignKey('EmployerProfile', on_delete=models.CASCADE, related_name='cv_accesses')
    candidate_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='cv_accesses')
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('employer_profile', 'candidate_profile')  # Added this line
        verbose_name = _("CV წვდომა")
        verbose_name_plural = _("CV წვდომები")
```

### 2. Fixed Repository Method
Updated `track_cv_access` method to handle existing duplicates gracefully:

```python
@staticmethod
def track_cv_access(employer_profile, candidate_profile):
    # First try to get an existing record
    cv_access = CVAccess.objects.filter(
        employer_profile=employer_profile,
        candidate_profile=candidate_profile
    ).first()
    
    if cv_access:
        # Update the accessed_at timestamp
        cv_access.save(update_fields=['accessed_at'])
    else:
        # Create a new record
        cv_access = CVAccess.objects.create(
            employer_profile=employer_profile,
            candidate_profile=candidate_profile
        )
        
    return cv_access
```

### 3. Updated View Method
Replaced direct `CVAccess.objects.create()` call in `view_cv_employer` with repository method:

```python
# Before
CVAccess.objects.create(
    employer_profile=employer_profile,
    candidate_profile=profile,
    accessed_at=timezone.now()
)

# After
from core.repositories.employer_repository import EmployerRepository
EmployerRepository.track_cv_access(employer_profile, profile)
```

### 4. Created Migration
Created migration `0062_add_cvaccess_unique_constraint.py` that:
- Removes existing duplicate records (keeps the most recent one)
- Adds the unique constraint to prevent future duplicates

## Files Modified
1. `core/models/application.py` - Added unique constraint
2. `core/repositories/employer_repository.py` - Fixed track_cv_access method
3. `core/views/profile_views.py` - Updated to use repository method
4. `core/migrations/0062_add_cvaccess_unique_constraint.py` - Migration to clean up duplicates and add constraint

## Testing
- Created and ran test script to verify the fix works correctly
- Test confirmed that only one record is created per employer-candidate pair
- Test confirmed that subsequent calls update the existing record instead of creating duplicates

## Deployment Steps
1. Deploy the code changes
2. Run the migration: `python manage.py migrate`
3. The migration will automatically clean up existing duplicates and add the constraint

## Prevention
The unique constraint will prevent this issue from occurring again in the future. Any attempt to create a duplicate record will now be rejected at the database level. 