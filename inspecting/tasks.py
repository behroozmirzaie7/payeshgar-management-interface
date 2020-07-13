import traceback

from inspecting import models
from monitoring import models as monitoring_models


def process_results(agent_ip, submission_time, results):
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
