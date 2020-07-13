import traceback
from datetime import timedelta, datetime

from celery import shared_task
from inspecting import models
from monitoring import models as monitoring_models


@shared_task
def process_results(agent_ip, submission_time, results):
    """
    Very simple task to process list of inspection results.
    In this version, it just save them in database and update agent last_activity

    """
    try:
        agent = monitoring_models.Agent.objects.get(ip=agent_ip)
        agent.last_activity = submission_time
        agent.save()

        models.HTTPInspectionResult.objects.bulk_create(
            [models.HTTPInspectionResult(
                inspection=r['inspection'],
                agent=agent,
                agent_ip=agent_ip,
                connection_status=r['connection_status'],
                status_code=r.get('status_code'),
                response_time=r.get('response_time'),
                byte_received=r.get('byte_received'),
                submitted_at=submission_time,
            ) for r in results]
        )
        # TODO watch for duplicates
        # TODO Do we need to send notification?
    except Exception as exp:
        print(traceback.format_exc())
        print(exp)


@shared_task
def generate_inspections():
    """
    Very simple inspection generator, this function will create future inspections to be used by the agents
    should be called periodically
    """
    inspections = []
    # TODO improve the loop and queries

    now = datetime.now()
    margin = now + timedelta(minutes=20)
    for endpoint in monitoring_models.Endpoint.objects.select_related('monitoring_policy').all():
        last_inspection = endpoint.inspections.last()
        if last_inspection is None:
            last_inspection = models.Inspection.objects.create(endpoint=endpoint, timestamp=now)
        if last_inspection.timestamp < margin:
            continue
        interval = timedelta(seconds=endpoint.monitoring_policy.interval)
        cur = last_inspection.timestamp
        while (cur - now) < timedelta(minutes=20):
            cur += interval
            inspections.append(models.Inspection(endpoint=endpoint, timestamp=cur))
    models.Inspection.objects.bulk_create(inspections)  # TODO Check for dupicates
