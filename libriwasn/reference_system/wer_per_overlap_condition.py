"""
Calculate the WER per overlap condition

Example calls:
python -m libriwasn.reference_system.transcribe --json_path /path/to/hyp_cpwer_per_reco.json
"""
import click
import paderbox as pb


@click.command()
@click.option(
    '--json_path',
    type=str,
    default=None,
    help='Path of the json-file with WER details per session.'
)
def main(json_path):
    msg = ('You have to define the path of the json file with the '
           'WER details per session.')
    assert json_path is not None, msg
    cpwer_details = pb.io.load_json(json_path)
    errors_total = 0
    length_total = 0
    for subset in ('0L', '0S', 'OV10', 'OV20', 'OV30', 'OV40'):
        errors = 0
        length = 0
        for session_id, cpwer_session in cpwer_details.items():
            if subset in session_id:
                errors += cpwer_session['errors']
                length += cpwer_session['length']
        print(f'{subset}: {errors / length * 100:.2f}% cpWER')
        errors_total += errors
        length_total += length
    print(f'Avg.: {errors_total / length_total * 100:.2f}% cpWER')


if __name__ == '__main__':
    main()

