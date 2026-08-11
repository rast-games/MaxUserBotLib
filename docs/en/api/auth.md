# Authentication internals

The authentication subsystem lets applications inspect or modify the initialized backend stack before mapper authentication. See the [authentication guide](../authentication.md#authflow-lifecycle) for a complete typed example.

## AuthFlow

::: pyromax.models.AuthFlow.AuthFlow
    options:
      show_root_heading: false

## AuthMiddlewareManager

::: pyromax.auth.manager.AuthMiddlewareManager
    options:
      members: true
      show_root_heading: false

## BaseAuthMiddleware

::: pyromax.auth.middleware.BaseAuthMiddleware
    options:
      members: true
      show_root_heading: false
