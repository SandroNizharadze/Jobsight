from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())
        
    def hard_delete(self):
        return super().delete()
        
    def alive(self):
        return self.filter(deleted_at=None)
        
    def deleted(self):
        return self.exclude(deleted_at=None)

class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.with_deleted = kwargs.pop('with_deleted', False)
        super().__init__(*args, **kwargs)
        
    def get_queryset(self):
        if self.with_deleted:
            return SoftDeletionQuerySet(self.model, using=self._db)
        return SoftDeletionQuerySet(self.model, using=self._db).filter(deleted_at=None)
        
    def hard_delete(self):
        return self.get_queryset().hard_delete()
        
    def deleted(self):
        return self.get_queryset().deleted()

class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name=_("წაშლის თარიღი"))
    
    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(with_deleted=True)
    
    class Meta:
        abstract = True
        
    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()
        
    def hard_delete(self):
        super().delete() 