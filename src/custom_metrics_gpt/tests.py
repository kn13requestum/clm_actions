from gpt_metrics import LevelStringParser, LevelsSampler


def test_parser():
    sample = 'start win start win start win start win start win start lose start win start win start win start amuletMoves amuletMoves win start win start boostHammer win start win start boostHammer win start boostSwapElements win start lose start win start horn lose start lose start lose start lose start win start boostCross win start additionalMoves boostCross win start additionalMoves win start additionalMoves lose start lose start boostCross amuletMoves win start amuletBomb boostSwapElements lose start lose start amuletBomb horn win start lose start lose start boostCross win start boostSwapElements win start boostHammer lose start horn win start win start lose start win start lose start lose start win start lose start win start win start win start win start lose start win start lose start lose start win start additionalMoves additionalMoves additionalMoves additionalMoves additionalMoves additionalMoves win start lose start win start win start win start win start boostHammer boostHammer boostHammer boostHammer boostHammer boostHammer lose start lose churn'
    parse_result = LevelStringParser.parse(sample)

    assert parse_result[-1].churn is True
    assert parse_result[-1].boosters['boostHammer'] == 6
    assert parse_result[-1].level_index == 38
    assert parse_result[27].win_rate == .5
    assert parse_result[27].loses == 1

    test_string = 'start win start win start win start win start win start lose start win'
    parse_result = LevelStringParser.parse(test_string)
    assert len(parse_result) == 6


def test_sampler():
    text_1 = 'start win start win start boostHammer boostHammer lose start lose start win'
    text_2 = 'start lose start win start boostCross amuletMoves win start boostCross lose churn'
    sampler_result = LevelsSampler([text_1, text_2]).to_levels

    assert sampler_result[0][2].loses == 2
    assert sampler_result[0][2].boosters['boostHammer'] == 2
    assert sampler_result[1][-1].win_rate == 0
    assert sampler_result[1][-1].churn is True
    assert sampler_result[1][2].boosters['boostCross'] == 1


test_parser()
test_sampler()