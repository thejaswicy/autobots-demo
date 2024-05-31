import { Octokit } from '@octokit/core';

async function addCollaborators(owner, repo, collaborators) {
  const octokit = new Octokit({
    auth: process.env.TOKEN
  });

  for (const collaborator of collaborators) {
    const { teams, permission } = collaborator;
    try {
      await octokit.request('PUT /orgs/tandfgroup/teams/{team_slug}/repos/{owner}/{repo}', {
        owner: owner,
        repo: repo,
        team_slug: teams,
        permission: permission,
        headers: {
          'X-GitHub-Api-Version': '2022-11-28'
        }
      });
      console.log(`Team ${teams} added as a collaborator to ${owner}/${repo} with permission ${permission}`);
    } catch (error) {
      console.error(`Failed to add team ${teams} as a collaborator to ${owner}/${repo}: ${error.message}`);
    }
  }
}

async function setBranchProtection(owner, repo, branch) {
  const octokit = new Octokit({
    auth: process.env.TOKEN
  });

  try {
    await octokit.request('PUT /repos/{owner}/{repo}/branches/{branch}/protection', {
      owner: owner,
      repo: repo,
      branch: branch,
      required_status_checks: {
        strict: true,
        contexts: []
      },
      enforce_admins: true,
      required_pull_request_reviews: {
        dismissal_restrictions: {
          "users": [
            "seantrane",
            "informa-ap-devops"
        ],
          teams: []
        },
        dismiss_stale_reviews: true,
        require_code_owner_reviews: true,
        required_approving_review_count: 2,
        require_last_push_approval: true,
        bypass_pull_request_allowances: {
          "users": [
            "seantrane",
            "informa-ap-devops"
        ],
          teams: []
        }
      },
      restrictions: {
        users: [],
        teams: [],
        apps: []
      },
      required_linear_history: false,
      allow_force_pushes: false,
      allow_deletions: false,
      block_creations: false,
      required_conversation_resolution: true,
      lock_branch: false,
      allow_fork_syncing: false,
      headers: {
        'X-GitHub-Api-Version': '2022-11-28'
      }
    });
      console.log(`Branch protection set for ${owner}/${repo}:${branch}`);
    } catch (error) {
      console.error(`Failed to set branch protection for ${owner}/${repo}:${branch}: ${error.message}`);
    }
  }

const owner = 'thejaswicy';
const repo = process.env.NEW_REPO_NAME;
const branch = 'main';

(async () => {
  try {
    // Parse collaborators from environment variable
    const collaborators = JSON.parse(process.env.COLLABORATORS);

    await addCollaborators(owner, repo, collaborators);
    await setBranchProtection(owner, repo, branch);
  } catch (error) {
    console.error('Error:', error);
  }
})();
