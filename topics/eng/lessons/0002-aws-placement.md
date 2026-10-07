---
title: AWS placement: where you stand against the MLA-C02 exam guide
subtitle: Pretest (about 25 minutes). One win: a map of which AWS foundations and exam domains you already have, so the AWS courses skip them.
crumb: Engineering career · Lesson 2 · AW000 placement
index: AWS placement pretest (MLA-C02 domains)
main: data-skip=true data-pretest=true
---
## How this works
This is a **pretest**: nothing here was taught yet, and none of it comes back in your review deck. Press **I don't know** rather
than guess; a guess makes the map wrong. You'll also be asked how sure you were after right answers. The questions follow the
official **MLA-C02 exam guide**: four domains, weighted 28% / 24% / 24% / 24% [1], plus a few AWS foundations the exam assumes.

**One thing to know first:** MLA-C02 is new. Its beta started on 29 September 2026; AWS lists general availability as "TBD" [2].
The C02 guide adds foundation models, RAG and agents to the older ML engineering content. And two services that older prep
material leans on, SageMaker Model Monitor and SageMaker Clarify, are now "no longer open to new customers" [3][4]; the C02 guide's
monitoring skills name CloudWatch generative AI observability and Amazon Bedrock evaluations instead [1]. So check the date of any
prep course or practice exam against the C02 guide.

## Warm-up: Vim (2 minutes)

::: callout
**Practical Vim, text objects: change inner word.** Rename the method to `choose_move` with as few keystrokes as you can. The cursor
starts on the `d` of `def`, in Normal mode. Par is 16.

Start: `def select_action(self, obs, legal, info):`

Target: `def choose_move(self, obs, legal, info):`
:::

::: free vim-v02
Your keystrokes (write Escape as `<Esc>`):
--- rubric
Checked by replaying: python3 scripts/vimcheck.py --drill topics/eng/vim-drills.json v02-ciw "<keys>". PASS = buffer equals target.
Par 16 (wciwchoose_move<Esc>). The tip: `ciw` changes the whole word wherever the cursor is inside it.
:::

## Part 1: AWS foundations the exam assumes

::: choice f-iam
A SageMaker AI training job only needs to read training data from one S3 bucket. What is the right way to give it access?
- [x] An execution role allowing only read actions on that one bucket
- [ ] An execution role that has the AWS managed AdministratorAccess policy attached
- [ ] Long-term access keys for an IAM user, stored in the script
- [ ] A bucket policy that allows public read access to the bucket
--- explain
Least privilege: an IAM role the job assumes, scoped to the actions and resource it needs (exam skills 4.3.2–4.3.3 [1]). Access keys
in code and public buckets are classic security findings; admin access breaks least privilege.
:::

::: number f-spot answer=2
How many minutes of warning does Amazon EC2 give before it stops or terminates a Spot Instance (interruption behavior not hibernate)?
--- explain
Two minutes: "a warning that is issued two minutes before Amazon EC2 stops or terminates your Spot Instance" [5]. That's why Spot
training needs checkpoints saved somewhere durable, such as S3.
:::

::: choice f-vpc
A SageMaker AI endpoint runs in a private subnet with no internet access and must read model artifacts from Amazon S3. What
lets it reach S3 without going over the internet?
- [x] An S3 VPC endpoint in that VPC
- [ ] An internet gateway attached to that VPC
- [ ] A larger instance type for the endpoint
- [ ] A public IP address on the endpoint
--- explain
A VPC endpoint (for S3, a gateway endpoint) keeps the traffic on AWS's network; an internet gateway or public IP is exactly what a
private subnet avoids. Exam skills 3.2.4 and 4.3.6 [1].
:::

::: choice f-parquet
A wide table with 300 columns is stored in S3, and training reads only 12 of them. Which storage format fits that access pattern best?
- [x] Apache Parquet, a columnar format
- [ ] CSV, a row-based text format
- [ ] JSON Lines, a row-based format
- [ ] Plain text, line per record
--- explain
Columnar formats (Parquet, ORC) let readers skip columns they don't need. Exam skill 1.1.5: choose formats "based on data access patterns" [1].
:::

## Part 2: the four exam domains

::: categorize d1-feature-store
**Domain 1, data preparation (28%).** SageMaker Feature Store has an online store and an offline store. Which one serves each need?
- Look up a customer's features while serving a prediction > Online store
- Assemble historical features to train a new model > Offline store
- Run batch inference over last month's records > Offline store
--- explain
"The online store enables real-time lookup of features for inference, while the offline store contains historical data for model
training and batch inference" [6].
:::

::: choice d2-bedrock
**Domain 2, model development (24%).** A team needs a document summarizer next week, has no labelled data, and doesn't want to host
models. What is the most direct fit?
- [x] Call a foundation model in Amazon Bedrock through its API
- [ ] Train a summarization model with a SageMaker AI built-in algorithm
- [ ] Fine-tune an open model, then host it on SageMaker AI
- [ ] Build a summarizer on EC2 GPUs with a custom container
--- explain
Exam skill 2.1.4: "Evaluate tradeoffs between custom solutions, managed services, pre-trained models, and FMs" [1]. No data, no
hosting, a short deadline: a managed FM. Fine-tuning becomes worth it when prompting falls short.
:::

::: choice d2-shadow
**Domain 2.** You want to test a new model on real production traffic, but users must keep getting the current model's answers. What
do you deploy the new model as?
- [x] A shadow variant next to the production variant
- [ ] A production variant with half of the traffic
- [ ] A separate endpoint that users can call directly
- [ ] A batch transform job over all yesterday's requests
--- explain
A shadow variant receives a copy of live requests, and its responses are logged, not returned. Exam skill 2.3.3: "Compare the
performance of shadow variants to production variants" [1]. Splitting traffic between production variants is an A/B test: users do
see the new model.
:::

::: categorize d3-inference
**Domain 3, deployment (24%).** Match each workload to the SageMaker AI inference option AWS recommends for it.
- Interactive requests that need low latency > Real-time inference
- Spiky traffic with idle periods; cold starts are acceptable > Serverless inference
- Payloads up to 1 GB that take up to an hour to process > Asynchronous inference
--- explain
From the SageMaker AI developer guide [7]: real-time is "ideal for inference workloads where you have interactive, low latency
requirements"; serverless suits "workloads which have idle periods between traffic spurts and can tolerate cold starts"; asynchronous
is "ideal for requests with large payload sizes (up to 1GB), long processing times (up to one hour), and near real-time latency
requirements".
:::

::: choice d3-registry
**Domain 3.** For audits, you must know which model version is in production, what data trained it, and who approved it. Which
AWS feature is built for that?
- [x] SageMaker Model Registry
- [ ] Amazon S3 Versioning
- [ ] AWS CodeCommit repositories
- [ ] Amazon ECR repositories
--- explain
Exam skill 3.3.6: "Manage model versions for repeatability and audits (for example, SageMaker Model Registry, MLflow on SageMaker
AI)" [1]. S3 versioning keeps file versions but no approval status or lineage.
:::

::: categorize d4-guardrails
**Domain 4, operations and security (24%).** Which Amazon Bedrock Guardrails filter fits each requirement?
- Mask customers' personal data in model responses > Sensitive information filter
- Block any question asking for investment advice > Denied topics
- Flag RAG answers that the retrieved documents don't support > Contextual grounding check
--- explain
From the Bedrock user guide [8]: sensitive information filters "block or mask sensitive information, such as personally identifiable
information (PII)"; denied topics block "a set of topics that are undesirable in the context of your application"; contextual
grounding checks "detect hallucinations in model responses if they are not grounded … in the source". Exam skill 4.3.9 [1].
:::

::: free d4-drift
**Domain 4.** Your fraud model's precision slowly drops over three months. Describe, in a few sentences, how you'd detect that the
production *inputs* have shifted away from the training data, and what you'd compare against.
--- rubric
Placement. Strong: capture production inputs (data capture / logging), compute a baseline from the training data (statistics and
constraints per feature), compare recent windows against it on a schedule (distribution distances such as PSI/KS, missing-value
rates), alert (e.g. CloudWatch alarms) and trigger retraining or investigation; separate data drift from concept drift (labels arrive
late). AWS names are a bonus, not required; Model Monitor is closed to new customers, so CloudWatch-based pipelines count fully.
:::

## Part 3: your experience and the exam date

::: free exp-self
Roughly how much hands-on time have you had with **SageMaker AI** and with **Amazon Bedrock** (none / tried it / used it at work)?
And your 2024 Solutions Architect course: finished, partly done, or not started?
--- rubric
Placement only. The guide's target candidate has "at least 1 year of experience using Amazon SageMaker AI, Amazon Bedrock, and other
AWS services for ML engineering" [1]. Use the answer to size AW101 (foundations) and AW201.
:::

::: free exp-date
When do you want to sit MLA-C02? The beta is running now ($75, 85 questions, 170 minutes; beta results come later than usual), and
general availability is "TBD" [2]. Give a target month, or "after GA".
--- rubric
No right answer. Record the target in curriculum.json (AW290) and NOTES.md; it sets the AWS lane's pace. If before ~January, AW101
shrinks to the essentials.
:::

Questions about anything here: ask me in chat. The AWS lane's rep for this lesson comes with AW101's first lesson, once the
pretest says where it starts.

## Sources
- AWS, *AWS Certified Machine Learning Engineer – Associate (MLA-C02) exam guide*: domains, weights and skills. <https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/machine-learning-engineer-associate-02.html>
- AWS Certification, MLA-C02 exam page (beta dates, format, price). <https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/>
- AWS, *SageMaker AI developer guide*, "Fairness, model explainability and bias detection with SageMaker Clarify" (availability note). <https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-configure-processing-jobs.html>
- AWS, *SageMaker AI developer guide*, "Data and model quality monitoring with Amazon SageMaker Model Monitor" (availability note). <https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html>
- AWS, *Amazon EC2 user guide*, "Spot Instance interruption notices". <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html>
- AWS, *SageMaker AI developer guide*, "Feature Store storage configurations". <https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store-storage-configurations.html>
- AWS, *SageMaker AI developer guide*, "Deploy models for inference". <https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html>
- AWS, *Amazon Bedrock user guide*, "Detect and filter harmful content by using Amazon Bedrock Guardrails". <https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html>
- Drew Neil, *Practical Vim*, 2nd ed. (in your library, id 59a28fc891).
