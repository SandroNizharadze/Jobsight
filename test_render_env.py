import os

print("Environment variables check:")
print(f"RENDER environment variable exists: {'Yes' if os.environ.get('RENDER') else 'No'}")
print(f"RENDER value: '{os.environ.get('RENDER', 'Not set')}'")

# Check which settings would be used
if os.environ.get('RENDER'):
    print("Using 'jobsy.render_settings'")
else:
    print("Using 'jobsy.settings'")

# Check render_settings.py contents
try:
    # Try to import render_settings to check its content
    import sys
    sys.path.insert(0, '.')
    from jobsy import render_settings
    
    # Check database settings
    print("\nrender_settings.py database configuration:")
    if hasattr(render_settings, 'DATABASES'):
        print(f"Database ENGINE: {render_settings.DATABASES['default'].get('ENGINE', 'Not set')}")
        print(f"Database HOST: {render_settings.DATABASES['default'].get('HOST', 'Not set')}")
        print(f"USE_SUPABASE: {getattr(render_settings, 'USE_SUPABASE', 'Not set')}")
    else:
        print("No DATABASES configuration found in render_settings")
except Exception as e:
    print(f"Error importing render_settings: {e}")

# Now let's check if supabase_settings would be imported in render_settings
print("\nChecking if render_settings imports supabase_settings:")
import inspect
try:
    from jobsy import render_settings
    content = inspect.getsource(render_settings)
    if "from .supabase_settings import" in content or "import supabase_settings" in content:
        print("render_settings does import supabase_settings")
    else:
        print("render_settings does NOT import supabase_settings directly")
        
    # If USE_SUPABASE is True, check if it would use supabase_settings
    if hasattr(render_settings, 'USE_SUPABASE') and render_settings.USE_SUPABASE:
        print("USE_SUPABASE is True in render_settings, so it should use supabase_settings")
    else:
        print("USE_SUPABASE is not True in render_settings")
except Exception as e:
    print(f"Error checking render_settings imports: {e}") 