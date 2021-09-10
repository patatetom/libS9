# libS9
Python library for IC Card Reader S9-BU-00-01 from Fongwah

![S9-BU-00-01](s9r.jpg)
![S9-BU-00-01](s9v.jpg)


## foreword

the library is intended to be used with `Python3` under `Linux`.
it only implements some functions from `libS8.so` and intended for `Mifare S50 tags` (classic 1k EV1).
only the `A key` is used.
except `readUID`, all the proposed functions expect a `block number` as input.
