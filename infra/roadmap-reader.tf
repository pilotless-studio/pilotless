# NOT APPLIED.
#
# pilotless-studio/harness was not readable from the checkout that wrote this
# file, so the live Workload Identity provider's attribute_condition is not
# copied here. Do not add a provider resource to this file: applying one would
# overwrite that condition.
#
# This is the least-privilege binding for decision (a). The GitHub Actions
# identity of pilotless-studio/pilotless may impersonate roadmap-reader and
# nothing else. roadmap-reader has no project roles. The server
# (pilotless-studio/app) accepts that email only for POST /gh/admin/roadmap_sync
# and forces dry_run. gha-deployer is not granted to this repository.
#
# The founder applies this in project pilotless-workspace, after reading the
# live provider. Cloud Run is already public; do not grant roles/run.invoker.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
  }
}

variable "project_id" {
  type    = string
  default = "pilotless-workspace"
}

variable "project_number" {
  type        = string
  description = "Numeric project number used in the workload identity principal."
}

variable "wif_pool_id" {
  type        = string
  description = "Existing GitHub Actions workload identity pool id. Do not create a second pool."
}

resource "google_service_account" "roadmap_reader" {
  project      = var.project_id
  account_id   = "roadmap-reader"
  display_name = "Roadmap reader"
  description  = "ID token for POST /gh/admin/roadmap_sync only. The server forces dry_run. No project roles."
}

resource "google_service_account_iam_member" "roadmap_reader_wif" {
  service_account_id = google_service_account.roadmap_reader.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${var.project_number}/locations/global/workloadIdentityPools/${var.wif_pool_id}/attribute.repository/pilotless-studio/pilotless"
}

# Equivalent commands. Do not run them from CI.
#
#   PROJECT=pilotless-workspace
#   gcloud iam service-accounts create roadmap-reader \
#     --project="$PROJECT" \
#     --display-name="Roadmap reader" \
#     --description="ID token for POST /gh/admin/roadmap_sync only. The server forces dry_run. No project roles."
#
#   gcloud iam workload-identity-pools providers describe PROVIDER_ID \
#     --project="$PROJECT" --location=global --workload-identity-pool=POOL_ID \
#     --format='yaml(attributeMapping,attributeCondition)'
#
# The provider must map attribute.repository from assertion.repository.
# If attribute_condition is an allowlist of assertion.repository values and
# pilotless-studio/pilotless is absent, add that one repository to the
# condition. Do not add it to the gha-deployer workloadIdentityUser members.
# If attribute_condition is already assertion.repository_owner ==
# "pilotless-studio", leave the provider alone. The binding below is the
# restriction.
#
#   gcloud iam service-accounts add-iam-policy-binding \
#     roadmap-reader@"$PROJECT".iam.gserviceaccount.com \
#     --project="$PROJECT" \
#     --role=roles/iam.workloadIdentityUser \
#     --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/pilotless-studio/pilotless"
#
# Then, on the pilotless-studio/pilotless repo (not the app repo):
#
#   gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER
#   gh secret set GCP_ROADMAP_READER_SERVICE_ACCOUNT
#
# GCP_WORKLOAD_IDENTITY_PROVIDER is the existing provider resource name.
# GCP_ROADMAP_READER_SERVICE_ACCOUNT is
# roadmap-reader@pilotless-workspace.iam.gserviceaccount.com.
