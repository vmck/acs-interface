# Features in VMCKV2

## Teaching Assistants features

There are specific actions that teaching assistants can run for an **asignment** or for a
**submission**.

### Assignment
  * Download last submissions for code review
  * Download specific last submission for code reivew
  * Run MOSS on the last submission - TODO
  * Run submissons multiple times - TODO

### Submission
  * Re-run submission in case there were some errors on the server side
  * Recompute score in case there was a change in the deadline

### Review homeworks:
The teaching assistants have the possibility to review -- add bonus points or substract points for a submission (it should be the last one uploaded by the student).

For adding points to a homework the format is the following:
```
+[number]: Text good review
```

Ex:
```
+12.0: The homework is fabulous
```

For substracing points from a homework the format is the following:
```
-[number]: Text bad review
```
Ex:
```
-10.0: Try to use defines for hardcoded values
```

## Student Features

### Download thee last submission
 * Select *List all submissions*
 * You can download only the submission that is linked with your account - as a student
