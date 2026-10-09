"""Single-attempt Stage D pre-label integrity receipt. Never opens ZIP members."""
import os,sys,time
from common import *
from integrity import verify_integrity
def main():
    check(not O.exists(),"Stage D already initialized; no retry without owner review")
    O.mkdir(parents=True)
    save(O/"FAILURE_LEDGER_INITIAL.json",{"at_utc":now(),"failures":[],"append_only_directory":"failures/"})
    event("STAGE_D_REGISTERED",labels_accessed=False,owner_sha256=sha(D/"OWNER_STAGE_D_AUTHORIZATION.md"))
    start=time.perf_counter()
    try:
        plan=source_check()
        check(git("status","--porcelain")=="","Pre-label code/plan/tests must be committed")
        result=verify_integrity()
        save(O/"PRE_LABEL_INTEGRITY_DETAILS.json",result)
        receipt={k:v for k,v in result.items() if k!="checks"}
        receipt.update(code_plan_commit=git("rev-parse","HEAD"),owner_authorization_sha256=plan["owner_authorization_sha256"],
            plan_sha256=sha(R/"configs/stage_D_execution_plan.json"),
            prelabel_source_sha256=plan["prelabel_source_sha256"],
            tests_sha256=sha(D/"DETERMINISTIC_TEST_RESULTS.xml"),
            direct_SOL_review_sha256=sha(D/"PRE_LABEL_DIRECT_SOL_REVIEW.md"),
            protected_integrity_details_sha256=sha(O/"PRE_LABEL_INTEGRITY_DETAILS.json"),
            event_registry_initialized=True,immutable_failure_logging_initialized=True,
            wall_seconds=time.perf_counter()-start)
        save(O/"PRE_LABEL_RECEIPT.json",receipt)
        save(D/"PRE_LABEL_INTEGRITY_RECEIPT.json",receipt)
        event("PRE_LABEL_GATES_PASS",receipt_sha256=sha(O/"PRE_LABEL_RECEIPT.json"),labels_accessed=False)
        print('PASS: pre-label identity, environment and source gates; official labels remain unopened',flush=True)
    except Exception as exc:
        failure(exc,"pre_label")
        save(D/"PRE_LABEL_BLOCKED.json",dict(status="STAGE_D_BLOCKED",at_utc=now(),labels_accessed=False,
            failure_type=type(exc).__name__))
        raise
if __name__=="__main__":main()
