## Scaling
1. Horizontally scale Main and SendMail Services
2. Add more partitions for kafka topic


## Integrating other features
1. Simply add a new function to send sms or notifications etc
(OR)
2. Create a seperate kafka topic for each of the other features and add a new consumer

## Edge Cases and Handling
### Email Sending Failure on Our Side: (handled)
Handling: Implement a retry mechanism to resend emails. Commit the offset only if the email is successfully sent.

### Email Sending Failure on Provider's Side: (handled)
Handling: Retry sending emails, and if retries are exhausted, move the message to a Dead Letter Queue (DLQ) for manual inspection.

### Invalid User Email: (handled)
Handling: Validate user email addresses before pushing to kafka.

### Fallback Provider: (not handled)
Handling: Configure multiple email service providers with a fallback mechanism. Switch to an alternative provider if the primary provider fails.

### User Opt-Out: (not handled)
Handling: Provide an option for users to opt-out of email notifications. Respect user preferences.

### Event Payload Size: (not a huge issue if event is predefined) (not handled)
Handling: Validate the size of the event payload to prevent excessively large messages from overwhelming the system.

### Email Throttling: (not handled)
Handling: Implement email throttling to avoid being flagged as spam by email service providers.