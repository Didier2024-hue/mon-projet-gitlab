# 🚀 GitLab CI/CD Pipeline — DevOps Exam Project

> 🔧 End-to-end reconstruction of a **GitLab CI/CD pipeline** with modular configuration, conditional execution rules, Docker image lifecycle management, and Git tag–based versioning.

---

## 🎯 Project Overview

The objective was to **design, restructure, and validate a complete GitLab CI/CD pipeline** following strict functional and best-practice requirements.

### Key skills demonstrated:

- ⚙️ Advanced GitLab CI/CD pipeline design
- 🔁 Conditional job execution using `rules`
- ♻️ Configuration reuse with `extends`
- 🐳 Docker image build, run, and push
- 🏷️ Git tag–based Docker image versioning
- 🧪 Automated testing for data pipelines
- 📦 Clean and maintainable repository structure

---

## 🏗️ Repository Structure

order/
├── .gitlab-ci.yml
├── configs/
│ ├── extends.yml
│ ├── transform.yml
│ ├── load.yml
│ ├── test.yml
│ ├── build.yml
│ ├── run.yml
│ └── push.yml
├── exec/
│ ├── transform/
│ │ ├── main.py
│ │ └── requirements.txt
│ └── load/
│ ├── main.py
│ └── requirements.txt
├── test/
│ ├── transform/
│ └── load/
└── pictures/

yaml
Copier le code

---

## 🔁 Pipeline Trigger Strategy

### 🔹 Global Workflow

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "push"
✅ This explicit rule ensures the pipeline is triggered on push events, avoiding ambiguous or implicit GitLab CI behavior.

♻️ Shared Configuration — configs/extends.yml
The default before_script has been removed and replaced with a reusable configuration using extends.

Benefits:
✅ No duplication across jobs

✅ Centralized environment setup

✅ Easier maintenance and scalability

✅ GitLab CI/CD best practices

All execution jobs (transform, load, test) inherit from this file.

🔄 Transform Stage — configs/transform.yml
📌 Job: exec_transform

Execution rules:
🟢 Source branch starts with:

transform_ or

load_

🟢 Pipeline source: merge_request_event

➡️ The job inherits its environment and setup from extends.yml.

📥 Load Stage — configs/load.yml
📌 Job: exec_load

Execution rules:
🟢 Source branch starts with load_

🟢 Pipeline source: merge_request_event

This stage handles data ingestion logic and is only validated through merge requests.

🧪 Testing Stage — configs/test.yml
📌 Jobs:

test_transform

test_load

Execution rules:
🔍 Triggered only on merge_request_event

♻️ Shared configuration via extends.yml

These jobs validate:

data transformation logic

load integrity

Python execution environments

🐳 Docker Build Stage — configs/build.yml
Execution rules:
🟢 Source branch starts with docker_

🟢 OR a Git tag is present

🟢 Pipeline source: merge_request_event

Docker images are built for:

order-transform

order-load

⚠️ Why Git Tags Matter
❌ Using CI_COMMIT_SHORT_SHA as a Docker image tag:

is not human-readable

does not represent a functional version

is not production-friendly

✅ Implemented solution:

Git annotated tags (e.g. v1.0)

One Git tag = one repository version = one Docker image version

Full traceability between code and containers

▶️ Run Stage — configs/run.yml
Execution rules:
🟢 Branch starts with docker_

🟢 Git tag exists

🟢 Merge request pipeline

⚠️ Jobs are marked with allow_failure: true for docker_* branches, enabling safe validation without blocking the pipeline.

📤 Push Stage — configs/push.yml
Standard jobs:
push_transform

push_load

➡️ Push Docker images tagged with the commit SHA (intermediate artifacts).

🆕 Tag-Based Push Jobs
📌 Additional jobs created:

push_transform_tag

push_load_tag

Behavior:
🔁 Create a new image using docker tag

🏷️ Docker tag = Git tag (e.g. v1.0)

📤 Push to the private GitLab Container Registry

🚦 Executed only if a Git tag is present

🏷️ Git Tag Creation
bash
Copier le code
git tag -a v1.0 -m "Version v1.0"
git push origin v1.0
➡️ This action triggers a fully versioned pipeline, validating the complete CI/CD workflow with production-ready Docker images.

📸 Pipeline Evidence
The pictures/ directory contains:

🖼️ Merge Request Pipeline
Pipeline triggered by a merge_request_event

🖼️ Tag Pipeline (v1.0)
Pipeline triggered by an annotated Git tag

🖼️ Container Registry Overview
Private GitLab registry with built images

🖼️ order-load:v1.0 Image
Tagged Docker image following DevOps best practices

The GitLab username is visible on the screenshots, as required.

✅ Conclusion
🎉 This project demonstrates:

A clean and modular GitLab CI/CD architecture

Advanced control of pipeline execution using rules

Proper Docker image versioning with Git tags

Strong alignment with professional DevOps standards
