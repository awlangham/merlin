import numpy as np

from merlin.installation import CurrentInstallation
from merlin.utilities import read_interval, get_joule_node


async def level_two(node_name, dataset, start, end):
    async with get_joule_node(node_name) as node:
        current_installation = CurrentInstallation(node)

        data = await read_interval(node_name, dataset, start, end)
        prep_data = data[:, 1:]

        matching_exemplar, match_score = await current_installation.find_matching_exemplar(prep_data)

        # if matching_exemplar is None:
        #     PA_ss, PB_ss, PC_ss = _extract_ss(prep_data[:, 0]), _extract_ss(prep_data[:, 8]), _extract_ss(prep_data[:, 16])
        #     QA_ss, QB_ss, QC_ss = _extract_ss(prep_data[:, 1]), _extract_ss(prep_data[:, 9]), _extract_ss(prep_data[:, 17])

        #     comb_match = await current_installation.combinatorial_match(PA_ss + PB_ss + PC_ss, QA_ss + QB_ss + QC_ss)
        #     print(comb_match)

    return matching_exemplar, match_score
