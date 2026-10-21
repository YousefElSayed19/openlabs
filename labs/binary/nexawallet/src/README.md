# src/ — source code location

The full, buildable Android Studio project for this challenge is **not duplicated** into this folder — it already lives one level up in this same repository, as its own complete Gradle project:

```
../../Mobile CTF Challenge (v2 Design)/
```

That folder contains everything needed to build the APK from scratch: the Gradle wrapper, `build.gradle` files, the Android manifest, and the full Kotlin source tree (`app/src/main/java/com/example/nexawallet/...`).

See `BUILD_INSTRUCTIONS.md` in this folder for the exact steps.

> **Reminder:** this `src/` pointer and the project it points to are for internal/organizer use only — never ship the source tree to participants. Only `bin/NexaWallet-debug.apk` goes to them.

## Source layout (for reference)

```
Mobile CTF Challenge (v2 Design)/app/src/main/java/com/example/nexawallet/
├── integrity/
│   └── IntegrityGate.kt           Gate 1 — unified Frida detection
├── authorization/
│   ├── ReviewState.kt             Gate 2 — clearance state
│   └── TransferAuthorizer.kt      limit check + clearance check + flag minting
├── session/
│   └── UserSession.kt             login/session state only
├── data/
│   └── LocalLedger.kt             local mock backend (balance, limit, accounts)
├── ui/
│   ├── LoginActivity.kt / RegisterActivity.kt / HomeActivity.kt
│   ├── TransferActivity.kt        main challenge screen
│   ├── WebTransferActivity.kt
│   ├── RestrictedActivity.kt      shown when Gate 1 fails
│   └── ReviewGateActivity.kt      the hidden screen (Gate 2)
└── network/
    ├── PinningConfig.kt
    └── WebViewTrustManager.kt
```
