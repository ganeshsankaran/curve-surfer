from django.shortcuts import render
from .forms import SearchForm
from .utils import *

def search(request):
    # Get courses, instructors, and quarters/years from DB
    # TODO: Cache
    cnums = get_cnums()
    instrs = get_instrs()
    qtrs = get_qtrs()

    if request.method == 'POST':
        form = SearchForm(request.POST)
        
        # Initialize context
        ctx = {
            'form': form,
            'cnums': cnums,
            'instrs': instrs,
            'qtrs': qtrs
        }

        if form.is_valid():
            # Post-process form
            d = split_qtr_and_yr(form.cleaned_data)

            # Get letter grade distribution
            letter_grade_dist = get_letter_grade_dist(d)
            ctx['letter_grade_dist'] = {
                'labels': list(letter_grade_dist.keys()),
                'data': list(letter_grade_dist.values()),
                'stats': get_letter_grade_dist_stats(d)
            }

            # Get chart/table data for other breakdowns (if applicable)
            # Only get the breakdown if the respective field in the 
            # input form is empty
            for_chart, for_table = get_avg_gpa_per_cnum(d)
            
            if for_chart and for_table:
                ctx['avg_gpa_per_cnum'] = {
                    'labels': list(for_chart.keys()),
                    'data': list(for_chart.values()),
                    'table': for_table
                }
            
            for_chart, for_table = get_avg_gpa_per_instr(d)

            if for_chart and for_table:
                ctx['avg_gpa_per_instr'] = {
                    'labels': list(for_chart.keys()),
                    'data': list(for_chart.values()),
                    'table': for_table
                }
            
            avg_gpa_per_qtr = get_avg_gpa_per_qtr(d)
                        
            if avg_gpa_per_qtr:
                ctx['avg_gpa_per_qtr'] = {
                    'labels': list(avg_gpa_per_qtr.keys()),
                    'data': list(avg_gpa_per_qtr.values())
                }

            return render(request, 'search.html', ctx)

        else:
            return render(request, 'search.html', ctx)

    return render(request, 'search.html', {
        'form': SearchForm(),
        'cnums': cnums,
        'instrs': instrs,
        'qtrs': qtrs
    })