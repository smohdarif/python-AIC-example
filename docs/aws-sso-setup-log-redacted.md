# AWS SSO Setup Log (Redacted)

This is a sanitized record of the AWS SSO setup steps.

```
sudo chown -R <your-user>:staff ~/.aws
chmod 700 ~/.aws
aws configure sso

SSO session name (Recommended): aiconfigdemo
SSO start URL [None]: https://<your-sso-start-url>/start/#
SSO region [None]: us-east-1
SSO registration scopes [sso:account:access]:

There are N AWS accounts available to you.
Using the account ID <your-account-id>
There are N roles available to you.
Using the role name "Administrator"
Default client Region [None]: us-east-1
CLI default output format (json if not specified) [None]: json
Profile name [Administrator-<account-id>]: aiconfigdemo

To use this profile, specify the profile name using --profile, as shown:
aws sts get-caller-identity --profile aiconfigdemo
```
