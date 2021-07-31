#!/usr/bin/env bash

set -euo pipefail

echo "Started at $(date '+%Y/%m/%d %H:%M:%S')"

# Fetch the projects
circleci-to-sqlite projects circleci.db
sqlite-utils tables --counts circleci.db

# Fetch jobs
sqlite-utils circleci.db \
  "select id, vcs_type || '/' || username || '/' || reponame as project_slug
   from projects
   where vcs_type = 'bitbucket' and username = 'aerobotics'" \
  --csv --no-headers | while IFS=, read project_id project_slug;
    do project_slug=$(echo $project_slug | tr -d '\r');
      circleci-to-sqlite jobs circleci.db $project_slug;
      sleep 1;
      # Fetch steps and actions
      # Only run for jobs that don't have any steps
      sqlite-utils circleci.db \
        "select build_num
         from jobs
         left join steps on steps.id = jobs.id
         where project_id = $project_id
         and steps.id is null
         order by build_num" \
        --csv --no-headers | while IFS=, read build_num;
          do build_num=$(echo $build_num | tr -d '\r');
            circleci-to-sqlite steps circleci.db $project_slug $build_num;
            sleep 1;
          done;
    done;

sqlite-utils tables --counts circleci.db
echo "Completed at $(date '+%Y/%m/%d %H:%M:%S')"
