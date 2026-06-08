# EasyBuild Install Software

Use this skill when a site or research group wants reproducible scientific
software builds through EasyBuild.

## Example

```bash
bash examples/easybuild-dry-run.sh foss-2023a.eb
```

After reviewing the dry-run plan, run the equivalent install command in a
user-owned prefix approved by your site.

## Safety Notes

EasyBuild can compile large dependency trees. Check quota, build directory, and
module output paths before running a full install.
