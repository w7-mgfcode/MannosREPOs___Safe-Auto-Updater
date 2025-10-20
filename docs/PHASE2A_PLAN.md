# Phase 2A Implementation Plan
## Helm Updater + Health Checks + Rollback

**Version**: 1.0
**Target**: v0.5.0 Beta
**Timeline**: 2-3 weeks
**Status**: Planning → Implementation

---

## 🎯 Objectives

Complete the core update loop:
1. ✅ Discover assets (DONE)
2. ✅ Detect versions (DONE)
3. ✅ Evaluate policies (DONE)
4. ⏳ **Execute updates** (THIS PHASE)
5. ⏳ **Validate health** (THIS PHASE)
6. ⏳ **Auto-rollback** (THIS PHASE)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                         │
│  Commands: update, rollback, watch                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Update Orchestrator                         │
│  • Policy enforcement                                    │
│  • Concurrent update management                          │
│  • Queue management                                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Helm Updater │ │   Watchtower │ │  K8s Direct  │
│              │ │  Integration │ │   Updater    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Health Check Engine                         │
│  • HTTP checks                                           │
│  • Kubernetes probes                                     │
│  • TCP checks                                            │
│  • Custom exec checks                                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    Success      Degraded      Failed
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Continue   │ │     Warn     │ │   Rollback   │
└──────────────┘ └──────────────┘ └──────┬───────┘
                                          ▼
                                  ┌──────────────┐
                                  │   Rollback   │
                                  │   Manager    │
                                  └──────────────┘
```

---

## 📦 Components to Implement

### 1. Helm Updater (`src/updater/helm_updater.py`)

**Responsibilities**:
- Execute Helm upgrades safely
- Support dry-run mode
- Track upgrade history
- Handle upgrade failures

**Key Methods**:
```python
class HelmUpdater:
    def __init__(self, config: KubernetesConfig)
    def upgrade(self, release: str, chart: str, version: str,
                namespace: str, dry_run: bool = False) -> UpdateResult
    def get_release_history(self, release: str, namespace: str) -> List[Release]
    def get_current_version(self, release: str, namespace: str) -> Optional[str]
    def validate_upgrade(self, release: str, chart: str, version: str) -> bool
```

**Safety Features**:
- ✅ Pre-upgrade validation (chart exists, version valid)
- ✅ Dry-run before actual upgrade
- ✅ Atomic upgrades (--atomic flag)
- ✅ Timeout protection
- ✅ History preservation
- ✅ Rollback on failure

**Dependencies**:
- `helm` CLI (via subprocess)
- Kubernetes client for validation
- State manager for tracking

---

### 2. Health Check Engine (`src/health/health_checker.py`)

**Responsibilities**:
- Validate service health post-update
- Support multiple check types
- Retry logic with exponential backoff
- Aggregate health status

**Key Methods**:
```python
class HealthChecker:
    def check(self, config: HealthCheckConfig, asset: Asset) -> HealthStatus
    def check_http(self, config: HTTPHealthCheck) -> bool
    def check_tcp(self, config: TCPHealthCheck) -> bool
    def check_exec(self, config: ExecHealthCheck) -> bool
    def check_kubernetes(self, asset: Asset) -> HealthStatus
    def wait_for_healthy(self, asset: Asset, timeout: int) -> bool
```

**Check Types**:

1. **HTTP Health Check**:
   - GET/POST to health endpoint
   - Validate status code (200-299)
   - Custom headers support
   - TLS/SSL support
   - Retry with backoff

2. **Kubernetes Health Check**:
   - Monitor pod readiness
   - Check rollout status
   - Validate replica counts
   - Detect crashloops

3. **TCP Health Check**:
   - Test port connectivity
   - Connection timeout
   - Retry logic

4. **Exec Health Check**:
   - Execute command in container
   - Validate exit code
   - Capture output

**Health Status**:
```python
@dataclass
class HealthStatus:
    healthy: bool
    ready_replicas: int
    total_replicas: int
    health_percentage: float
    checks_passed: List[str]
    checks_failed: List[str]
    message: str
```

---

### 3. Rollback Manager (`src/rollback/rollback_manager.py`)

**Responsibilities**:
- Detect update failures
- Execute automatic rollback
- Track rollback history
- Prevent infinite rollback loops

**Key Methods**:
```python
class RollbackManager:
    def __init__(self, config: RollbackConfig)
    def should_rollback(self, health: HealthStatus) -> bool
    def rollback_helm(self, release: str, namespace: str,
                      revision: Optional[int] = None) -> RollbackResult
    def record_rollback(self, asset_id: str, reason: str)
    def get_rollback_count(self, asset_id: str, window: int = 3600) -> int
    def is_rollback_loop(self, asset_id: str) -> bool
```

**Safety Mechanisms**:
- ✅ Failure threshold detection
- ✅ Monitoring duration window
- ✅ Max rollback attempts
- ✅ Loop prevention
- ✅ Audit logging
- ✅ Notification on rollback

**Rollback Triggers**:
1. Health check failure (below threshold)
2. Pod crash loops
3. Deployment timeout
4. Manual trigger

---

### 4. Update Orchestrator (`src/updater/orchestrator.py`)

**Responsibilities**:
- Coordinate updates across multiple assets
- Enforce concurrent update limits
- Manage update queue
- Apply update windows

**Key Methods**:
```python
class UpdateOrchestrator:
    def __init__(self, config: AutoUpdateConfig)
    def queue_update(self, asset: Asset, target_version: str)
    def process_queue(self) -> List[UpdateResult]
    def can_update_now(self) -> bool  # Check update window
    def get_queue_status(self) -> QueueStatus
    def cancel_update(self, asset_id: str)
```

**Features**:
- ✅ Concurrent update limit
- ✅ Update window enforcement
- ✅ Priority queue (security > bug fix > feature)
- ✅ Dependency management
- ✅ Pause/resume capability

---

### 5. CLI Commands

#### `update` Command

```bash
safe-updater update <asset_name> [OPTIONS]

Options:
  --to-version TEXT       Target version
  --namespace, -n TEXT    Kubernetes namespace
  --dry-run              Simulate without executing
  --force                Skip policy gates
  --wait                 Wait for completion
  --timeout INTEGER      Timeout in seconds
```

**Implementation**:
```python
@cli.command()
@click.argument('asset_name')
@click.option('--to-version', required=True)
@click.option('--namespace', '-n', default='default')
@click.option('--dry-run', is_flag=True)
@click.option('--force', is_flag=True)
@click.option('--wait', is_flag=True, default=True)
@click.option('--timeout', default=300)
def update(asset_name, to_version, namespace, dry_run, force, wait, timeout):
    """Execute update for specified asset"""
```

#### `rollback` Command

```bash
safe-updater rollback <asset_name> [OPTIONS]

Options:
  --to-version TEXT       Rollback to specific version
  --namespace, -n TEXT    Kubernetes namespace
  --revision INTEGER      Helm revision number
```

**Implementation**:
```python
@cli.command()
@click.argument('asset_name')
@click.option('--to-version')
@click.option('--namespace', '-n', default='default')
@click.option('--revision', type=int)
def rollback(asset_name, to_version, namespace, revision):
    """Rollback a failed update"""
```

---

## 🔄 Update Workflow

### Normal Update Flow

```
1. User triggers update (or auto-detection)
   ↓
2. Load asset from state
   ↓
3. Evaluate policy (diff gate)
   ↓
4. [If approved] Add to update queue
   ↓
5. Check update window & concurrent limit
   ↓
6. Execute pre-update validation
   ↓
7. [DRY RUN] Simulate update
   ↓
8. [REAL] Execute Helm upgrade (atomic)
   ↓
9. Wait for rollout completion
   ↓
10. Execute health checks
    ↓
11. [If healthy] Mark success, update state
    ↓
12. [If unhealthy] Trigger rollback (see below)
```

### Rollback Flow

```
1. Detect failure (health check or timeout)
   ↓
2. Check rollback count (prevent loops)
   ↓
3. Log rollback decision
   ↓
4. Execute Helm rollback to previous revision
   ↓
5. Wait for rollout completion
   ↓
6. Execute health checks
   ↓
7. [If healthy] Mark rollback success
   ↓
8. [If still unhealthy] Alert & require manual intervention
   ↓
9. Update state & audit log
   ↓
10. Send notification
```

---

## 🛡️ Safety Mechanisms

### 1. Pre-Update Validation

```python
def validate_before_update(asset: Asset, target_version: str) -> ValidationResult:
    checks = [
        validate_version_format(target_version),
        validate_chart_exists(asset.chart, target_version),
        validate_policy_approval(asset.current_version, target_version),
        validate_resource_availability(),
        validate_no_pending_updates(asset.id),
    ]
    return all(checks)
```

### 2. Atomic Updates

```bash
# Helm upgrade with atomic flag
helm upgrade --install my-app my-chart \
  --version 1.2.3 \
  --atomic \
  --timeout 5m \
  --wait \
  --namespace production
```

**Atomic flag ensures**:
- Auto-rollback on failure
- Wait for all resources
- No partial updates

### 3. Health Monitoring

```python
def monitor_health_post_update(asset: Asset, duration: int = 300):
    start_time = time.time()
    while time.time() - start_time < duration:
        health = health_checker.check_kubernetes(asset)

        if health.health_percentage < failure_threshold:
            return False  # Trigger rollback

        if health.healthy and health.ready_replicas == health.total_replicas:
            return True  # Success

        time.sleep(30)  # Check every 30 seconds

    return False  # Timeout
```

### 4. Loop Prevention

```python
def is_rollback_loop(asset_id: str, window: int = 3600) -> bool:
    """Detect if asset is stuck in update-rollback loop"""
    rollbacks = get_recent_rollbacks(asset_id, window)

    if len(rollbacks) >= 3:
        # 3+ rollbacks in 1 hour = loop detected
        return True

    return False
```

---

## 🧪 Testing Strategy

### Unit Tests

1. **Helm Updater Tests**:
   - Mock helm CLI calls
   - Test dry-run mode
   - Test error handling
   - Test history retrieval

2. **Health Checker Tests**:
   - Mock HTTP requests
   - Mock Kubernetes API
   - Test retry logic
   - Test timeout handling

3. **Rollback Manager Tests**:
   - Test failure detection
   - Test rollback execution
   - Test loop prevention
   - Test audit logging

### Integration Tests

1. **Update Workflow**:
   - Deploy test Helm chart
   - Execute update
   - Validate health checks
   - Verify state updates

2. **Rollback Workflow**:
   - Trigger failed update
   - Verify auto-rollback
   - Check final state

3. **Concurrent Updates**:
   - Queue multiple updates
   - Verify limit enforcement
   - Check completion order

### E2E Tests

1. **Full Update Cycle**:
   - Scan assets
   - Detect version change
   - Evaluate policy
   - Execute update
   - Monitor health
   - Verify success

2. **Failure & Recovery**:
   - Induce update failure
   - Verify auto-rollback
   - Check audit trail
   - Validate notifications

---

## 📊 Success Metrics

### Functional
- ✅ Helm upgrades execute successfully
- ✅ Health checks validate correctly
- ✅ Auto-rollback prevents downtime
- ✅ Loop prevention works
- ✅ Concurrent updates managed

### Performance
- ⏱️ Update execution < 5 minutes (typical)
- ⏱️ Health check latency < 30 seconds
- ⏱️ Rollback execution < 60 seconds

### Quality
- 🧪 Test coverage ≥ 80%
- 🔒 Security scans pass
- 📝 Documentation complete
- ✅ CI/CD passes

---

## 📅 Implementation Timeline

### Week 1: Core Update Logic

**Days 1-2**: Helm Updater
- [ ] Implement HelmUpdater class
- [ ] Add dry-run support
- [ ] Add error handling
- [ ] Unit tests

**Days 3-4**: Health Checks
- [ ] Implement HealthChecker class
- [ ] HTTP health checks
- [ ] Kubernetes health checks
- [ ] Unit tests

**Day 5**: Integration
- [ ] Connect updater + health checker
- [ ] Integration tests

### Week 2: Rollback & CLI

**Days 1-2**: Rollback Manager
- [ ] Implement RollbackManager
- [ ] Failure detection
- [ ] Loop prevention
- [ ] Unit tests

**Days 3-4**: CLI Commands
- [ ] Add `update` command
- [ ] Add `rollback` command
- [ ] Add `history` command
- [ ] CLI tests

**Day 5**: Orchestrator
- [ ] Implement UpdateOrchestrator
- [ ] Queue management
- [ ] Update window logic

### Week 3: Testing & Polish

**Days 1-2**: Integration Tests
- [ ] Full update workflow tests
- [ ] Rollback scenario tests
- [ ] Concurrent update tests

**Days 3-4**: Documentation
- [ ] Update API.md
- [ ] Add examples
- [ ] Update README
- [ ] Deployment guide

**Day 5**: Release Preparation
- [ ] Final testing
- [ ] Security audit
- [ ] Performance testing
- [ ] v0.5.0 release

---

## 🚨 Risk Mitigation

### Risk 1: Helm CLI Dependency

**Risk**: Helm CLI might not be available
**Mitigation**:
- Check for helm at startup
- Provide clear error messages
- Document installation requirements

### Risk 2: Network Failures

**Risk**: Health checks might fail due to network issues
**Mitigation**:
- Retry logic with exponential backoff
- Configurable timeouts
- Distinguish between transient & permanent failures

### Risk 3: Rollback Failures

**Risk**: Rollback might also fail
**Mitigation**:
- Preserve previous state
- Manual rollback option
- Alert on rollback failure
- Escalation procedures

### Risk 4: Race Conditions

**Risk**: Concurrent updates to same asset
**Mitigation**:
- Lock mechanism per asset
- State validation before update
- Atomic state updates

---

## 📚 Dependencies

### New Python Packages

```python
# Already in requirements.txt:
# - kubernetes
# - pyyaml
# - pydantic
# - requests

# No new dependencies needed!
```

### External Tools

- **Helm 3.x**: Required for Helm updates
- **kubectl**: Optional (for manual verification)

---

## 🎯 Definition of Done

Phase 2A is complete when:

- [ ] All unit tests pass (≥80% coverage)
- [ ] Integration tests pass
- [ ] CI/CD pipeline passes
- [ ] Security scans clean
- [ ] Documentation updated
- [ ] CodeRabbit review approved
- [ ] Manual testing complete
- [ ] Example deployments work
- [ ] Performance metrics met
- [ ] Ready for v0.5.0 beta release

---

## 🚀 Next Phase (Phase 2B)

After Phase 2A completion:

1. **Watchtower Integration** - Docker container updates
2. **Advanced Health Checks** - TCP, Exec checks
3. **Prometheus Metrics** - Observability
4. **Watch Mode** - Continuous monitoring
5. **Notification Webhooks** - Slack, Discord alerts

---

**Plan Status**: ✅ Complete
**Ready to Implement**: Yes
**Estimated Effort**: 2-3 weeks
**Target Release**: v0.5.0 Beta (Dec 2025)
