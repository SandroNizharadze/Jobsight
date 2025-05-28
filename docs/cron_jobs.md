# Cron Jobs Setup

This document explains how to set up cron jobs for Jobsy to ensure proper maintenance of the site.

## List of Cron Jobs

### 1. Update Expired Jobs

This job updates the status of expired jobs and handles Premium+ access removal when jobs expire. It should run daily.

```bash
# Run every day at 3:00 AM
0 3 * * * cd /path/to/jobsy && python manage.py update_expired_jobs >> /var/log/jobsy/cron.log 2>&1
```

### 2. Clean Orphaned S3 Files

This job cleans up S3 files that are no longer referenced in the database. It's recommended to run this weekly.

```bash
# Run every Sunday at 4:00 AM
0 4 * * 0 cd /path/to/jobsy && python manage.py clean_orphaned_s3_files --days 7 >> /var/log/jobsy/cron.log 2>&1
```

## Setting Up Cron Jobs

### On Linux/Unix systems:

1. Edit the crontab:
   ```bash
   crontab -e
   ```

2. Add the cron job entries (modify paths as needed):
   ```bash
   # Jobsy Cron Jobs
   0 3 * * * cd /path/to/jobsy && python manage.py update_expired_jobs >> /var/log/jobsy/cron.log 2>&1
   0 4 * * 0 cd /path/to/jobsy && python manage.py clean_orphaned_s3_files --days 7 >> /var/log/jobsy/cron.log 2>&1
   ```

3. Save and exit.

### On Windows (using Task Scheduler):

1. Open Task Scheduler
2. Create a new Basic Task
3. Set trigger to daily at 3:00 AM
4. Set action to start a program
5. Program/script: `python`
6. Add arguments: `manage.py update_expired_jobs`
7. Start in: `C:\path\to\jobsy`

## Deployment with Docker

If you're using Docker, add these commands to your deployment scripts or use a specialized container for cron jobs:

```dockerfile
# Example crontab file for Docker
FROM jobsy_web

# Install cron
RUN apt-get update && apt-get -y install cron

# Add crontab file
COPY crontab /etc/cron.d/jobsy-cron

# Give execution permission
RUN chmod 0644 /etc/cron.d/jobsy-cron

# Apply cron job
RUN crontab /etc/cron.d/jobsy-cron

# Create log directory
RUN mkdir -p /var/log/jobsy

# Run cron in foreground
CMD cron -f
```

## Monitoring

Check the log file periodically to ensure the cron jobs are running successfully:

```bash
tail -f /var/log/jobsy/cron.log
``` 