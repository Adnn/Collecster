from advideogame import models

def find_games(system):
    all_games = models.Occurrence.objects.filter(release__concept__primary_nature="GAME")
                            
    games_with_system = all_games.filter(release__system_specification__interfaces_specification__systeminterfacedetail__advertised_system=system)

    # For the immaterial occurrences without a system on their release, that are composing other releases.
    games_no_system = all_games.filter(release__system_specification=None) \
                               .filter(release__releasecomposition__from_release__system_specification__interfaces_specification__systeminterfacedetail__advertised_system=system)

    result = games_with_system | games_no_system
    return result


def print_games(games):
    for game in games:
        print("{}".format(game))

