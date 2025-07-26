# Autonomy Core Implementation Plan

> **Status**: Core PRD Requirements Analysis  
> **Target**: Complete all F-0, F-1, F-2, F-3 requirements  
> **Timeline**: 6-8 weeks for MVP completion

---

## 📊 Current Status Analysis

### ✅ **COMPLETED Features**

#### **F-0 (Core) - 100% Complete**
- ✅ **F-0-1**: Instant CLI bootstrap (`pipx install autonomy`)
- ✅ **F-0-2**: Device-Flow OAuth (GitHub authentication)
- ✅ **F-0-3**: OS-native secret storage (keychain + file fallback)
- ✅ **F-0-4**: Board Bootstrap (GitHub Projects v2 fields)
- ✅ **F-0-5**: Slack Bot Setup (basic OAuth and webhook infrastructure)

#### **F-1 (MVP Beta) - 80% Complete**
- ✅ **F-1-1**: Task Retrieval (`autonomy next` with priority ranking)
- ✅ **F-1-2**: Status Update (`autonomy update` with notes)
- ✅ **F-1-6**: Slack Commands (`/autonomy next`, `/autonomy update`, `/autonomy status`)
- ✅ **F-1-8**: Instrumentation (basic metrics tracking)

#### **F-2 (Core Enhancement) - 60% Complete**
- ✅ **F-2-2**: Ranking Engine (weighted scoring)
- ✅ **F-2-3**: Pin/Unpin Toggle (`/autonomy pin|unpin`)

#### **F-3 (Core Security) - 100% Complete**
- ✅ **F-3-1**: Identity Mgmt (GitHub OAuth)

---

## 🚧 **MISSING Features (Priority Order)**

### **HIGH PRIORITY - Critical for MVP**

#### **F-1-3: Hierarchy Sync** ⚠️ **PARTIAL**
**Status**: Basic implementation exists, needs completion
**What we have**: `HierarchyManager` class with tree building and parent creation
**What's missing**:
- [ ] **Tasklists API integration** - Update parent issues with tasklists
- [ ] **CLI command** - `autonomy hierarchy sync` command
- [ ] **Auto-maintenance** - Trigger hierarchy sync on issue updates
- [ ] **Orphan warnings** - Alert when orphan count > threshold

**Tasks**:
1. Complete `create_tasklist_hierarchy()` method integration
2. Add CLI command for manual hierarchy sync
3. Integrate with issue update workflow
4. Add orphan detection and warnings

#### **F-1-5: Undo System** ⚠️ **PARTIAL**
**Status**: Basic undo exists, missing shadow-branch PR functionality
**What we have**: `UndoManager` with basic operation reversal
**What's missing**:
- [ ] **Shadow-branch PR creation** - Create PR for multi-issue edits
- [ ] **JSON diff hash embedding** - Embed hash in PR comments
- [ ] **Slack undo command** - `/autonomy undo <hash>` in Slack
- [ ] **Configurable commit window** - Default 5 commits, configurable

**Tasks**:
1. Implement shadow-branch PR creation for multi-issue edits
2. Add JSON diff hash generation and embedding
3. Create Slack undo command handler
4. Add configurable commit window (default 5)

#### **F-1-4: Backlog Doctor** ✅ **COMPLETE**
**Status**: Fully implemented with nightly digest
**What we have**: Complete `BacklogDoctor` with stale/duplicate/oversized detection
**What's missing**: Nothing - this feature is complete

#### **F-1-7: Slack Notifications** ✅ **COMPLETE**
**Status**: Fully implemented with nightly digest and metrics
**What we have**: Complete notification system with `BacklogDoctorNotifier`, `MetricsDashboard`
**What's missing**: Nothing - this feature is complete

### **MEDIUM PRIORITY - Core Enhancement**

#### **F-2-1: Overrides Listener** ❌ **MISSING**
**Status**: Not implemented
**What we need**:
- [ ] **GitHub webhook handler** - Capture drag/field edits
- [ ] **Overrides table** - Store override data
- [ ] **Webhook endpoint** - `/webhook/github` endpoint
- [ ] **Override tracking** - Track manual vs automated changes

**Tasks**:
1. Create GitHub webhook handler
2. Implement overrides storage system
3. Add webhook endpoint to API server
4. Integrate with ranking engine

### **LOW PRIORITY - Nice to Have**

#### **Enhanced Metrics (F-1-8 improvement)**
**Status**: Basic metrics exist, needs enhancement
**What we have**: Basic `MetricsCollector` with daily reports
**What's missing**:
- [ ] **WAU tracking** - Weekly active users
- [ ] **Approval rate tracking** - Bot edit approval metrics
- [ ] **Time-to-task metrics** - Average time to get next task
- [ ] **Enhanced dashboards** - Better Slack reporting

**Tasks**:
1. Enhance WAU tracking in metrics collector
2. Add approval rate calculation
3. Improve time-to-task measurement
4. Enhance Slack dashboard formatting

---

## 🎯 **Implementation Roadmap**

### **Week 1-2: Critical MVP Features**
1. **Complete Hierarchy Sync** (F-1-3)
   - Finish Tasklists API integration
   - Add CLI command
   - Integrate with issue workflow
   - Add orphan warnings

2. **Complete Undo System** (F-1-5)
   - Implement shadow-branch PR creation
   - Add JSON diff hash embedding
   - Create Slack undo command
   - Add configurable commit window

### **Week 3-4: Core Enhancement**
3. **Implement Overrides Listener** (F-2-1)
   - Create GitHub webhook handler
   - Implement overrides storage
   - Add webhook endpoint
   - Integrate with ranking

4. **Enhance Metrics** (F-1-8 improvement)
   - Improve WAU tracking
   - Add approval rate metrics
   - Enhance time-to-task measurement
   - Better Slack dashboards

### **Week 5-6: Testing & Polish**
5. **Comprehensive Testing**
   - Unit tests for all new features
   - Integration tests for webhooks
   - End-to-end workflow testing
   - Performance testing

6. **Documentation & Examples**
   - Update user guide with new features
   - Add examples for hierarchy sync
   - Document undo system usage
   - Create troubleshooting guide

---

## 🔧 **Technical Implementation Details**

### **Hierarchy Sync Implementation**
```python
# Add to CLI main.py
def cmd_hierarchy_sync(manager: WorkflowManager, args) -> int:
    """Sync issue hierarchy and update tasklists."""
    from ..tasks.hierarchy_manager import HierarchyManager
    
    hm = HierarchyManager(manager.issue_manager)
    result = hm.maintain_hierarchy()
    
    if result["created"]:
        print(f"✓ Created {len(result['created'])} parent issues")
    if result["orphans"]:
        print(f"⚠️  Found {len(result['orphans'])} orphan issues")
    
    return 0
```

### **Undo System Enhancement**
```python
# Add to UndoManager
def create_shadow_branch_pr(self, operations: List[Dict]) -> str:
    """Create shadow branch PR with JSON diff hash."""
    # Implementation for shadow-branch PR creation
    pass

def embed_diff_hash(self, pr_number: int, hash_value: str) -> bool:
    """Embed JSON diff hash in PR comment."""
    # Implementation for hash embedding
    pass
```

### **Overrides Listener**
```python
# Add to API server
@app.post("/webhook/github")
def github_webhook(request: Request):
    """Handle GitHub webhooks for override tracking."""
    # Implementation for webhook handling
    pass
```

---

## 📋 **Testing Strategy**

### **Unit Tests**
- [ ] `test_hierarchy_sync_cli()` - Test hierarchy sync command
- [ ] `test_shadow_branch_pr()` - Test shadow branch PR creation
- [ ] `test_webhook_override_tracking()` - Test webhook override capture
- [ ] `test_enhanced_metrics()` - Test improved metrics collection

### **Integration Tests**
- [ ] `test_complete_undo_workflow()` - Test full undo workflow
- [ ] `test_hierarchy_maintenance()` - Test hierarchy auto-maintenance
- [ ] `test_webhook_integration()` - Test webhook with GitHub events

### **End-to-End Tests**
- [ ] `test_mvp_workflow()` - Test complete MVP workflow
- [ ] `test_slack_integration()` - Test all Slack commands and notifications

---

## 🎯 **Success Criteria**

### **MVP Completion (Week 2)**
- [ ] All F-1 requirements implemented and tested
- [ ] Hierarchy sync working with Tasklists API
- [ ] Undo system with shadow-branch PRs
- [ ] Basic metrics and notifications working

### **Core Enhancement (Week 4)**
- [ ] All F-2 requirements implemented
- [ ] Overrides listener capturing manual changes
- [ ] Enhanced metrics with WAU and approval rates
- [ ] Comprehensive test coverage (>90%)

### **Production Ready (Week 6)**
- [ ] All features thoroughly tested
- [ ] Documentation complete and up-to-date
- [ ] Performance optimized
- [ ] Ready for pilot deployment

---

## 📈 **Risk Mitigation**

### **High Risk Items**
1. **GitHub API Rate Limits** - Implement proper rate limiting and caching
2. **Webhook Security** - Validate webhook signatures and implement proper auth
3. **Data Consistency** - Ensure undo operations are atomic and reversible

### **Medium Risk Items**
1. **Slack API Changes** - Use stable Slack SDK and handle API versioning
2. **Performance at Scale** - Monitor and optimize for larger repositories
3. **User Adoption** - Provide clear documentation and examples

---

## 🚀 **Next Steps**

1. **Immediate (This Week)**:
   - Complete hierarchy sync implementation
   - Start shadow-branch PR functionality
   - Add missing CLI commands

2. **Short Term (Next 2 Weeks)**:
   - Complete undo system
   - Implement overrides listener
   - Enhance metrics collection

3. **Medium Term (Next Month)**:
   - Comprehensive testing
   - Documentation updates
   - Performance optimization

---

*This plan focuses on completing the core PRD requirements for a production-ready MVP. Advanced features are reserved for the Pro version.* 