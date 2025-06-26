from merlin.utilities import async_run

@async_run
async def level_two(self, start_ts: int, end_ts: int):
    data = await self.get_transient(start_ts, end_ts)
    prep_data = data[:, 1:]

    matching_exemplar, match_score = await self.find_matching_exemplar(prep_data)

    # if matching_exemplar is None:
    #     PA_ss, PB_ss, PC_ss = _extract_ss(prep_data[:, 0]), _extract_ss(prep_data[:, 8]), _extract_ss(prep_data[:, 16])
    #     QA_ss, QB_ss, QC_ss = _extract_ss(prep_data[:, 1]), _extract_ss(prep_data[:, 9]), _extract_ss(prep_data[:, 17])

    #     comb_match = await current_installation.combinatorial_match(PA_ss + PB_ss + PC_ss, QA_ss + QB_ss + QC_ss)
    #     print(comb_match)

    return matching_exemplar, match_score
