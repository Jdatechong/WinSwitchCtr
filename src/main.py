from src.gui.gui import main_gui
from src.services.win_event_handler import start_foreground_event_handler, create_observer_from_func
from src.services.store_occurrences import Occurrences as occStore

if __name__ == '__main__':
    # create data storage object
    occ_list = occStore()
    # start window switch hook and handler
    start_foreground_event_handler(create_observer_from_func(occ_list.increment_count))
    # start gui
    main_gui(occ_list)
