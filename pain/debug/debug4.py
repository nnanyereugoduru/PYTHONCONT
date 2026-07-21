'''Migrated this from an old script, didn't get to fully vet it before I got pulled onto something else. Rough spots I remember:

Priority ordering felt right in my gut but I never actually verified high-priority jobs run before low-priority ones — just assumed it worked.
Marking a job "complete" that was never added in the first place did something weird, didn't chase it.
Retry logic — jobs are supposed to get removed after too many failures, but I have a nagging feeling the max-retry check isn't quite catching them at the right moment.
get_jobs_by_status felt fine in isolation but combining it with complete_job in the same run gave me a result I didn't expect once. Might've been me, might not.'''





class TaskQueue:
    def __init__(self, max_retries=3):
        self.jobs = {}  # job_id -> dict with status, priority, retries
        self.max_retries = max_retries
        self.next_id = 1

    def add_job(self, name, priority=1):
        
        job_id = self.next_id
        self.jobs[job_id] = {
            'name': name,
            'priority': priority,
            'status': 'pending',
            'retries': 0
        }
        self.next_id += 1
        
        
        return job_id

    def get_next_job(self):
        
        pending = [j for j in self.jobs.values() if j['status'] == 'pending']
        if not pending:
            return None
        sorted_jobs = sorted(pending, key=lambda j: j['priority'], reverse=True)
        return sorted_jobs[0]

    def fail_job(self, job_id):
        job = self.jobs[job_id]
        job['retries'] += 1
        if job['retries'] >= self.max_retries:
            job['status'] = 'failed'
        else:
            job['status'] = 'pending'
            
        

    def complete_job(self, job_id):
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'complete'
        else:
            print('invalid job id')

    def get_jobs_by_status(self, status):
        result = []
        for job_id, job in self.jobs.items():
            if job['status'] == status:
                result.append(job)
        return result
    # debug tester
    def print_jobs(self):
        for job_id, job in self.jobs.items():
            print(f"Job ID: {job_id}, Name: {job['name']}, Status: {job['status']}, Priority: {job['priority']}, Retries: {job['retries']}")

def main():
    q = TaskQueue(max_retries=2)

    id1 = q.add_job("Send email", priority=3)
    id2 = q.add_job("Backup database", priority=1)
    id3 = q.add_job("Generate report", priority=2)

    print("Next job to run (should be highest priority):", q.get_next_job()['name'])

    print("\nSimulating failures on 'Backup database'...")
    q.fail_job(id2)
    q.fail_job(id2)
    #q.fail_job(id2) # at 3 it declares ID2 as failing
    #q.fail_job(id2)
    #print("Backup database status:", q.jobs[id2]['status'])
    #print("Backup database retries:", q.jobs[id2]['retries'])

    #print("\nCompleting a job that doesn't exist...")
    #q.complete_job(id1)
    q.get_jobs_by_status('pending')

    #print("\nCompleting Generate report...")
    id5 = 'Name'
    q.complete_job(id5)
    print()
    print("Pending jobs:", [j['name'] for j in q.get_jobs_by_status('pending')])
    print("Complete jobs:", [j['name'] for j in q.get_jobs_by_status('complete')])
    print()
    print("Next job to run (should be highest priority):", q.get_next_job()['name'])
    q.print_jobs()
if __name__ == "__main__":
    main()