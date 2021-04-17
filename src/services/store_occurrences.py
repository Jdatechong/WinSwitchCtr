import pandas as pd
import datetime
from apscheduler.schedulers.background import BackgroundScheduler


def round_datetime_to_minute(dt):
    dt = dt - datetime.timedelta(seconds=dt.second, microseconds=dt.microsecond)
    return dt


class Occurrences:
    def __init__(self):
        self.update_graph = (lambda: print('should not enter'))
        now_datetime = datetime.datetime.now()
        now_floored = round_datetime_to_minute(now_datetime)
        self.curr_occ_list = pd.DataFrame({'Datetime': [now_floored], 'Cnt': [0]})
        self.curr_occ_list = self.curr_occ_list.set_index(['Datetime'])
        self.last_date_added = now_floored
        self.session_begin_datetime = now_datetime
        self.max_cnt = 0
        self.session_cnt = 0
        self.schedule_task_on_minute()

    def set_update_graph(self, update_func):
        self.update_graph = update_func

    def schedule_task_on_minute(self):
        # print('scheduling tasks')
        sched = BackgroundScheduler()
        sched.start()

        def job_function():
            return self.add_new_date_entry(entry_offset=datetime.timedelta(minutes=1))

        sched.add_job(job_function, 'cron', day_of_week='mon-sun', hour='0-23', minute='0-59', second='58')


    def increment_count(self):
        now_floored = round_datetime_to_minute(datetime.datetime.now())
        if now_floored in self.curr_occ_list.index:
            curr_val = self.curr_occ_list.at[now_floored, "Cnt"]
            new_val = curr_val + 1
            self.curr_occ_list.at[now_floored, "Cnt"] = new_val
            if self.max_cnt < new_val:
                self.max_cnt = new_val
        else:
            self.curr_occ_list.at[now_floored, "Cnt"] = 1
            if self.max_cnt < 1:
                self.max_cnt = 0
        self.session_cnt = self.session_cnt + 1
        self.update_graph()

    def get_occ_list(self):
        return self.curr_occ_list

    def get_max_cnt(self):
        return self.max_cnt

    def add_new_date_entry(self, entry_offset=datetime.timedelta(minutes=0)):
        now_floored = round_datetime_to_minute(datetime.datetime.now() + entry_offset)
        if now_floored not in self.curr_occ_list.index:
            self.curr_occ_list.at[now_floored, "Cnt"] = 0
        self.update_graph()
        return

    def get_curr_cnt(self):
        return self.session_cnt

    def get_session_run_time_in_minutes(self):
        curr_time = datetime.datetime.now()
        curr_run_time = curr_time - self.session_begin_datetime
        return curr_run_time.total_seconds() / 60

    # todo: add saving functionality
    '''
    def save_df_to_storage(self):
        # storage_loc = str(pathlib.Path(__file__).parent.absolute()) + '/saves/saved_df.csv'
        # storage_loc = storage_loc.replace('\\', '/')
        print(f'{storage_loc}')
        self.curr_occ_list.to_csv()
    '''
