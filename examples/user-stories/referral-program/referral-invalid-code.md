# Referral Invalid Code

As an invited friend,
I want a clear message when a referral link is invalid or expired,
so that I understand why my discount was not applied and can still continue shopping.

## Acceptance Criteria
1. Opening an expired or unknown referral link shows the message "This referral offer is no longer valid" on the signup page
2. The message includes a "Continue without discount" action that proceeds to normal signup
3. No reward is granted to any customer when the referral code is invalid
4. The invalid-code event is logged with the attempted code and timestamp

## Notes / Context
- Epic: docs/epics/referral-program.md
- Unhappy path of docs/user-stories/referral-share-link.md

## Open Questions
- Should expired links be renewable by the original sharer? (product decision pending)
