from django.shortcuts import render


def custom_404_view(request, exception=None):
    """
    Custom 404 handler rendering AnchorPod branded not-found page.
    """
    return render(request, "404.html", status=404)


def custom_500_view(request):
    """
    Custom 500 handler rendering AnchorPod branded server error page.
    """
    return render(request, "500.html", status=500)
