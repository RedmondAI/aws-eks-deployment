# GitHub Actions Setup Guide

This guide walks you through setting up GitHub Actions to automatically run Pulumi for your EKS infrastructure.

## Overview

Two workflows are configured:
- **PR Workflow**: Runs `pulumi preview` on pull requests to show planned changes
- **Merge Workflow**: Runs `pulumi up` when PRs are merged to main/master to apply changes

## Prerequisites

- GitHub repository with admin access
- AWS credentials (access key + secret key)
- Pulumi Cloud account (for state management)
- Twingate account credentials
- Git credentials for private repository access

---

## Basic Setup (Using AWS Access Keys)

Follow these steps to get GitHub Actions working with your existing AWS credentials.

## Step 1: Get Pulumi Access Token

1. Log in to [Pulumi Cloud](https://app.pulumi.com/)
2. Go to **Settings** → **Access Tokens**
3. Click **Create Token**
4. Give it a name (e.g., `github-actions-eks`)
5. Copy the token (you won't be able to see it again)

## Step 2: Gather Twingate Credentials

You need three Twingate values:
- **TWINGATE_NETWORK_ID**: Your Twingate network ID
- **TWINGATE_NETWORK**: Your Twingate network name
- **TWINGATE_API_KEY**: API key for Twingate access

Get these from your Twingate admin console or contact your Twingate administrator.

## Step 3: Gather Git Credentials

For accessing private repositories (like `https://github.com/RedmondAI/eks-bootstap.git`):
- **GIT_USER**: GitHub username or organization
- **GIT_PASS**: GitHub Personal Access Token (PAT) with `repo` scope

To create a PAT:
1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Select scope: `repo` (Full control of private repositories)
4. Generate and copy the token

## Step 4: Add GitHub Repository Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these **9 secrets**:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret access key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region for your deployment | `us-east-2` |
| `PULUMI_ACCESS_TOKEN` | Pulumi access token from Step 1 | `pul-abc123...` |
| `TWINGATE_NETWORK_ID` | Twingate network ID from Step 2 | `your-network-id` |
| `TWINGATE_NETWORK` | Twingate network name from Step 2 | `your-network-name` |
| `TWINGATE_API_KEY` | Twingate API key from Step 2 | `your-api-key` |
| `GIT_USER` | GitHub username from Step 3 | `your-username` |
| `GIT_PASS` | GitHub PAT from Step 3 | `ghp_abc123...` |

**Important**: Do NOT set `AWS_ROLE_TO_ASSUME` when using access keys.

## Step 5: Verify Workflow Configuration

The workflows are located at:
- `.github/workflows/pulumi-pr.yml` - Runs on pull requests
- `.github/workflows/pulumi-merge.yml` - Runs on merge to main/master

Verify the branch names match your repository:
- If your default branch is `main`, no changes needed
- If your default branch is `master` or something else, update `pulumi-merge.yml`

## Step 6: Test the Setup

### Test PR Preview

1. Create a new branch: `git checkout -b test-pulumi-ci`
2. Make a small change (e.g., add a comment to `__main__.py`)
3. Commit and push: `git push origin test-pulumi-ci`
4. Open a pull request
5. Check the **Actions** tab - you should see "Pulumi PR Preview" running
6. Review the Pulumi preview output in the workflow logs

### Test Merge Apply

1. If the preview looks good, merge the PR
2. Check the **Actions** tab - you should see "Pulumi Apply on Merge" running
3. Verify the infrastructure changes were applied

## Troubleshooting

### "Error assuming role"
- Verify the trust policy in Step 1.2 has the correct repository name
- Check that the OIDC provider exists in your AWS account
- Ensure `AWS_ROLE_TO_ASSUME` secret has the correct ARN

### "Stack not found"
- The workflows automatically create the `juno` stack if it doesn't exist
- Verify `PULUMI_ACCESS_TOKEN` is correct
- Check Pulumi Cloud to see if the stack exists

### "Permission denied" errors
- Review IAM permissions attached to the GitHub Actions role
- Check CloudTrail logs to see which specific permissions are missing
- Add required policies to the role

### Twingate or Git errors
- Verify all Twingate secrets are correct
- Test Git credentials locally: `git clone https://$GIT_USER:$GIT_PASS@github.com/RedmondAI/eks-bootstap.git`
- Ensure the PAT has `repo` scope

### "AWS_PROFILE not found"
- This is expected in CI - the workflows set `AWS_PROFILE=cosmos` for compatibility with your code
- AWS credentials come from OIDC role assumption, not from profiles

## Security Best Practices

1. **Least Privilege**: Only grant the minimum AWS permissions needed
2. **Restrict by Branch**: Update the trust policy to restrict to specific branches if needed
3. **Rotate Tokens**: Regularly rotate Pulumi tokens, PATs, and API keys
4. **Review Logs**: Monitor GitHub Actions logs for suspicious activity
5. **Use Environments**: Consider using GitHub Environments for additional approval gates on production deployments

## Manual Workflow Trigger

Both workflows can be triggered manually:
1. Go to **Actions** tab
2. Select the workflow
3. Click **Run workflow**
4. Choose the branch and click **Run workflow**

## Next Steps

- Set up branch protection rules to require PR reviews
- Configure Slack/email notifications for workflow failures
- Add additional validation steps (linting, security scanning)
- Consider using GitHub Environments for staging/production separation

## Support

If you encounter issues:
1. Check the workflow logs in the **Actions** tab
2. Review AWS CloudTrail for permission errors
3. Verify all secrets are correctly set
4. Test Pulumi commands locally with the same environment variables

---

## Extending with AWS OIDC (Advanced)

For enhanced security, you can replace AWS access keys with OIDC authentication. This eliminates long-lived credentials in GitHub.

### Benefits of OIDC

- **No long-lived credentials**: No access keys stored in GitHub
- **Automatic rotation**: Temporary credentials expire automatically
- **Fine-grained control**: Restrict by repository, branch, or environment
- **Audit trail**: Better CloudTrail logging with role assumption

### Migration Steps

#### 1. Create OIDC Identity Provider (one-time per AWS account)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**Note**: If the provider already exists, you'll see an error - that's fine, continue to step 2.

#### 2. Create IAM Role for GitHub Actions

Create a trust policy file `github-trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:*"
        }
      }
    }
  ]
}
```

**Replace**:
- `YOUR_ACCOUNT_ID` with your AWS account ID (e.g., `123456789012`)
- `YOUR_ORG/YOUR_REPO` with your GitHub org and repo (e.g., `RedmondAI/aws-eks-deployment`)

Create the role:

```bash
aws iam create-role \
  --role-name GitHubActionsEKSDeployment \
  --assume-role-policy-document file://github-trust-policy.json
```

#### 3. Attach Required Permissions

Attach the same permissions your current AWS user has. At minimum:

```bash
# EKS permissions
aws iam attach-role-policy \
  --role-name GitHubActionsEKSDeployment \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy

# ECR permissions
aws iam attach-role-policy \
  --role-name GitHubActionsEKSDeployment \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

# Add additional policies as needed for:
# - EC2 (VPC, subnets, security groups)
# - IAM (creating roles for EKS nodes)
# - S3 (if using S3 buckets)
# - Secrets Manager (if storing secrets)
```

**Tip**: Review your `__main__.py` to identify all AWS services used.

#### 4. Get the Role ARN

```bash
aws iam get-role --role-name GitHubActionsEKSDeployment --query 'Role.Arn' --output text
```

Copy the ARN (e.g., `arn:aws:iam::123456789012:role/GitHubActionsEKSDeployment`)

#### 5. Update GitHub Secrets

In your GitHub repository → **Settings** → **Secrets and variables** → **Actions**:

1. **Add** this new secret:
   - `AWS_ROLE_TO_ASSUME` = the role ARN from step 4

2. **Delete** these secrets (no longer needed):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

3. **Keep** all other secrets:
   - `AWS_REGION`
   - `PULUMI_ACCESS_TOKEN`
   - `TWINGATE_NETWORK_ID`
   - `TWINGATE_NETWORK`
   - `TWINGATE_API_KEY`
   - `GIT_USER`
   - `GIT_PASS`

#### 6. Update Workflow Permissions

The workflows already support OIDC. Verify they have these permissions (already configured):

```yaml
permissions:
  id-token: write  # Required for OIDC
  contents: read
```

#### 7. Test OIDC Authentication

1. Create a test branch and PR
2. Check the **Actions** tab
3. Verify the workflow successfully assumes the role
4. Look for "Assuming role..." in the AWS credentials step

### Troubleshooting OIDC

**"Error assuming role"**
- Verify trust policy has correct repository name (case-sensitive)
- Check OIDC provider exists: `aws iam list-open-id-connect-providers`
- Ensure `AWS_ROLE_TO_ASSUME` has the correct ARN

**"Access denied" errors**
- Review IAM permissions attached to the role
- Check CloudTrail logs for specific permission failures
- Compare with permissions your AWS access keys had

**"Token validation failed"**
- Verify the thumbprint in the OIDC provider is correct
- Ensure `id-token: write` permission is set in workflow

### Restricting by Branch (Optional)

To only allow OIDC from specific branches, update the trust policy condition:

```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": [
    "repo:YOUR_ORG/YOUR_REPO:ref:refs/heads/main",
    "repo:YOUR_ORG/YOUR_REPO:ref:refs/heads/master"
  ]
}
```

### Rollback to Access Keys

If you need to revert:

1. Re-add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets
2. Delete `AWS_ROLE_TO_ASSUME` secret
3. The workflows will automatically use access keys
