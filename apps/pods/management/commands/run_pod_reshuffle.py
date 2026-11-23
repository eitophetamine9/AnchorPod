from django.core.management.base import BaseCommand
from apps.pods.services import run_pod_reshuffle


class Command(BaseCommand):
    help = "Scans for dormant members (inactive 3+ days) and re-balances pods via PodReshuffleLog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=3,
            help="Number of days of consecutive inactivity before member rotation (default: 3).",
        )

    def handle(self, *args, **options):
        days = options["days"]
        self.stdout.write(f"Initiating pod health scan with {days}-day inactivity cutoff...")

        results = run_pod_reshuffle(days_inactive=days)

        self.stdout.write(
            self.style.SUCCESS(
                f"Reshuffle complete! Rotated {results['rotated_inactive_count']} inactive members, "
                f"consolidated {results['reallocated_count']} solitary active members."
            )
        )
