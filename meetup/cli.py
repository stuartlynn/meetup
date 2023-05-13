from typing import Optional
from typing_extensions import Annotated
from meetup.geo import  load_user_locations 
from meetup.clustering import MeetingPointMethod, generate_group_meeting_points, run_clustering, format_results
from meetup.vis import generate_report
from meetup.logging import logInfo
from meetup.caching import RunCache
from pathlib import Path
import typer 


from meetup import __app_name__, __version__

app = typer.Typer()
@app.command()
def clear(
    run_name: Annotated[str,typer.Argument(help ="The output name for this run. Once the script has run you will find your results in {run_name}/results.csv and if visualization is requested {run_name}/outputname.png")],
    )->None:
    RunCache.set_run_name(run_name)
    RunCache.clear_cache()

@app.command()
def run(
    user_locations: Annotated[str, typer.Argument(help="The file containing the user locations. We require that this file is a csv format and that it contains columns for userid, latitude and longitude")],
    run_name: Annotated[str,typer.Argument(help ="The output name for this run. Once the script has run you will find your results in {run_name}/results.csv and if visualization is requested {run_name}/outputname.png")],
    max_optomization_iterations: Annotated[Optional[int] , typer.Option(
        help="Maxinum number of iterations to use to try and get groups between the specified min and max occupancy. After this the script will give up and output the results"
        )] =None,
    min_occupancy: Annotated[Optional[int], typer.Option(
        help="Minimum group occupancy to target. This is not guarenteed",
        )] = None,
    max_occupancy: Annotated[Optional[int],typer.Option(
        help="Maximum group occupancy to target. This is not guarenteed"
        )] = None,
    user_id_col: Annotated[Optional[str], typer.Option(
        help="Name of the userId column in the input dataset. Defaults to \"user_id\" "
        )] ="user_id",
    lat_col: Annotated[Optional[str] , typer.Option(
        help="Name of the latitude column in the input dataset. Defaults to \"latitude\" "
        )] ="latitude",
    lng_col: Annotated[Optional[str], typer.Option(
        help="Name of the logitude column in the input dataset. Defaults to \"logitude\" "
        )] = "longitude",
    meeting_point_method: Annotated[Optional[MeetingPointMethod], typer.Option(
        help="Meeting point method, one of 'centroid', 'centroid_snapped_to_street_network or landmark"
        )] = MeetingPointMethod.CENTROID,
    visualize_results: Annotated[bool, typer.Option(
        help="Visualize results"
        )] = False,
    ) -> None: 
        logInfo(f"[bold yellow]💾[/bold yellow] Generating groups for input file [bold white]{user_locations}[/bold white]")

        RunCache.set_run_name(run_name)
        outputDir = Path(run_name)

        if not outputDir.exists():
            outputDir.mkdir()

        if(min_occupancy is not None):
            logInfo(f"Will try to ensure that every group has more than {min_occupancy} users")

        if(max_occupancy is not None):
            logInfo(f"Will try to ensure that no group has more than {max_occupancy}")
        
        locations = load_user_locations(user_locations,lat_col,lng_col,user_id_col)

        groupAssignments = run_clustering(locations, min_occupancy, max_occupancy, max_optomization_iterations)
        groupMeetingPoints = generate_group_meeting_points(groupAssignments, meeting_point_method) 
        results = format_results(groupAssignments, groupMeetingPoints)
         
        results.to_csv(outputDir / "results.csv", index=False)

        if visualize_results:
            generate_report(results, outputDir / "report.index")


