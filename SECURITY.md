# Security Policy

## Reporting

Thank you for taking the time to responsibly disclose any problems you find.

**Do not file public issues as they are open for everyone to see!**

All security vulnerabilities in `gd.py` should be reported by email
to [security@nekit.dev][Security Email].
Your report will be acknowledged within 24 hours, and you will receive a more
detailed response within 48 hours indicating the next steps in handling your report.

You can encrypt your report using our public key:
[`BB2D8194464001E0B9B60EB8741A1EAD20FFDE8A`][Security Key].
This key is also available on [MIT's Key Server][MIT Key Server]
and [reproduced below](#security-key).

After the initial reply to your report, the core team will try to keep you
informed of the progress being made towards a fix and official announcement.
These updates will be sent at least every five days. In reality, this is
more likely to be every 24-48 hours.

## Disclosure Policy

`gd.py` has a 5-step disclosure process:

1. The security report is received and is assigned a primary handler.
   This person will coordinate the fix and release process.

2. The problem is confirmed and a list of all affected versions is determined.

3. Code is audited to find any potential similar problems.

4. Fixes are prepared for all releases which are still under maintenance.
   These fixes are not committed to the public repository but rather
   held locally pending the announcement.

5. On the embargo date, the changes are pushed to the public repository
   and new builds are deployed.

This process can take some time, especially when coordination is required
with maintainers of other projects. Every effort will be made to handle
the issue in as timely a manner as possible, however it is important that
we follow the release process above to ensure that the disclosure is handled
in a consistent manner.

## Security Key

```text
-----BEGIN PGP PUBLIC KEY BLOCK-----

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
1oYi7ft0FnZ67Wnk5+E+
=VRe2
-----END PGP PUBLIC KEY BLOCK-----
```

## Attribution

This Security Policy is adapted from [Rust's Security Policy][Rust Security Policy].

[Security Email]: mailto:security@nekit.dev
[Security Key]: https://nekit.dev/keys/security
[MIT Key Server]: https://pgp.mit.edu/pks/lookup?op=index&search=0xBB2D8194464001E0B9B60EB8741A1EAD20FFDE8A
[Rust Security Policy]: https://rust-lang.org/policies/security
