import threading
import ImageAnalysis
import PeopleFinderAuto

if __name__ == "__main__":
    # Define functions to run each script in a separate thread
    def run_image_analysis():
        ImageAnalysis.poll_new_images()

    def run_people_finder_auto():
        PeopleFinderAuto.poll_folder()

    # Create threads for each script
    image_analysis_thread = threading.Thread(target=run_image_analysis)
    people_finder_auto_thread = threading.Thread(target=run_people_finder_auto)

    # Start both threads
    image_analysis_thread.start()
    people_finder_auto_thread.start()

    # Join threads to wait for their completion
    image_analysis_thread.join()
    people_finder_auto_thread.join()
