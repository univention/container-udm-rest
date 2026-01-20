# Patches

The patches are tracked in the `ucs` repository in the branch
`nubus/patches/udm-rest-api`.

They can be exported from git in the following way if you have a clone of the
`ucs` repository:

```
git format-patch 5.2-4
```

The value `5.2-4` is the base branch on which the patches are based.

The output should be a bunch of patch files:

```
0001-fix-disabling-structured-logging-restores-original-f.patch
```
