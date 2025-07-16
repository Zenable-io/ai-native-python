#!/usr/bin/env bash
set -euo pipefail

# Check if run ID is provided as argument
if [[ $# -eq 1 ]]; then
  GITHUB_RUN_ID="$1"
elif [[ -z "${GITHUB_RUN_ID:-}" ]]; then
  echo "Usage: $0 <run_id>"
  echo "Or set GITHUB_RUN_ID environment variable"
  exit 1
fi

# Ensure required environment variables
: "${GITHUB_REPOSITORY:?Missing GITHUB_REPOSITORY}"
: "${GITHUB_TOKEN:?Missing GITHUB_TOKEN}"

# Use the GH CLI with auth
export GH_TOKEN="$GITHUB_TOKEN"

# Create a temp dir for logs
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

cd "$tmpdir"

# Get list of jobs in the run
echo "Fetching jobs for run $GITHUB_RUN_ID..."
jobs_json=$(gh api \
  -H "Accept: application/vnd.github+json" \
  "/repos/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}/jobs" \
  --paginate)

# Extract completed job IDs (excluding the current job if GITHUB_JOB is set and always excluding "Test Scripts")
if [[ -n "${GITHUB_JOB:-}" ]]; then
  completed_jobs=$(echo "$jobs_json" | jq -r --arg current_job "$GITHUB_JOB" '.jobs[] | select(.status == "completed") | select(.name != $current_job) | select(.name != "Test Scripts") | .id')
else
  completed_jobs=$(echo "$jobs_json" | jq -r '.jobs[] | select(.status == "completed") | select(.name != "Test Scripts") | .id')
fi

if [[ -z "$completed_jobs" ]]; then
  echo "::warning::No completed jobs found to scan"
  exit 0
fi

# Download logs for each completed job
echo "Downloading logs for completed jobs..."
for job_id in $completed_jobs; do
  job_name=$(echo "$jobs_json" | jq -r --arg id "$job_id" '.jobs[] | select(.id == ($id | tonumber)) | .name')
  echo "  Downloading logs for job: $job_name (ID: $job_id)"

  # Create directory for this job's logs
  mkdir -p "$job_name"

  # Download the job's log
  if gh api \
    -H "Accept: application/vnd.github+json" \
    "/repos/${GITHUB_REPOSITORY}/actions/jobs/${job_id}/logs" \
    --method GET > "$job_name/log.txt" 2>/dev/null; then
    echo "    ✓ Downloaded $(wc -l < "$job_name/log.txt") lines"
  else
    echo "    ✗ Failed to download logs"
    rm -rf "$job_name"
  fi
done

# Scan for lines with "deprecated", "warning:", or "error"
echo "Scanning logs for warnings, deprecations, and errors..."

# Process each log file and collect results
results_file=$(mktemp)

find . -type f -name "*.txt" | while IFS= read -r logfile; do
  # Get the job name from the directory structure
  job_name=$(dirname "$logfile" | sed 's|^\./||' | cut -d'/' -f1)

  # Search for patterns with context
  while IFS= read -r line; do
    # Extract line number and content
    line_num=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)

    # Sanitize content to prevent command injection and log poisoning
    sanitized_content=$(echo "$content" | tr -d '\n\r' | cut -c1-200)

    # Determine the type of issue and output both annotation and count
    if echo "$content" | grep -qiE '\berror\b'; then
      echo "::error file=$job_name,line=$line_num::$sanitized_content"
      echo "error" >> "$results_file"
    elif echo "$content" | grep -qiE '\bwarning:'; then
      echo "::warning file=$job_name,line=$line_num::$sanitized_content"
      echo "warning" >> "$results_file"
    elif echo "$content" | grep -qiE '\bdeprecated\b'; then
      echo "::warning file=$job_name,line=$line_num::$sanitized_content"
      echo "deprecated" >> "$results_file"
    fi
  done < <(grep -niE '(\berror\b|warning:|deprecated)' "$logfile" 2>/dev/null || true)
done

# Count results
error_count=$(grep -c "error" "$results_file" 2>/dev/null || echo 0)
warning_count=$(grep -c "warning" "$results_file" 2>/dev/null || echo 0)
deprecated_count=$(grep -c "deprecated" "$results_file" 2>/dev/null || echo 0)

# Summary
echo
echo "=== Log Scan Summary ==="
echo "Errors found: $error_count"
echo "Warnings found: $warning_count"
echo "Deprecation notices found: $deprecated_count"
echo "Total issues: $((error_count + warning_count + deprecated_count))"

# Clean up temp file
rm -f "$results_file"

# Exit with success even if issues were found
exit 0
