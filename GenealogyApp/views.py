from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter, landscape
# from reportlab.pdfgen import canvas
import csv, json
# from .models import Person
from django.contrib.auth import views as auth_views
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

# from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
# from django.http import HttpResponse
from .models import Person, FamilyGroup
import csv

def user_login(request):
    print("bbb")
    if request.method == 'POST':
        print("aa")
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            print("hh")
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            print("Form is invalid:")
            print(form.errors)  # This will print detailed error messages in the console
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Person, FamilyGroup
import json

def build_two_level_tree(person, family_group):
    spouse = f" ({person.spouse.first_name} {person.spouse.last_name})" if person.spouse else ""
    tree = {
        "id": person.id,
        "name": f"{person.first_name} {person.last_name}{spouse}",
        "children": []
    }

    children = Person.objects.filter(family_groups=family_group).filter(
        father=person) | Person.objects.filter(family_groups=family_group).filter(mother=person)

    for child in children.distinct():
        spouse = f" ({child.spouse.first_name} {child.spouse.last_name})" if child.spouse else ""
        tree["children"].append({
            "id": child.id,
            "name": f"{child.first_name} {child.last_name}{spouse}",
            "children": []
        })

    return tree

# from googletrans import Translator

# translator = Translator()

# def translate_to_malayalam(text):
#     try:
#         translation = translator.translate(text, dest='ml')
#         return translation.text
#     except Exception:
#         return ""  # Fallback in case translation fails

# def build_two_level_tree(person, family_group):
#     # English name
#     full_name_en = f"{person.first_name} {person.last_name}"
#     spouse_name_en = f"({person.spouse.first_name} {person.spouse.last_name})" if person.spouse else ""

#     # Malayalam name
#     full_name_ml = translate_to_malayalam(full_name_en)
#     spouse_name_ml = translate_to_malayalam(person.spouse.first_name + " " + person.spouse.last_name) if person.spouse else ""

#     tree = {
#         "id": person.id,
#         "name_en": full_name_en,
#         "spouse_en": spouse_name_en,
#         "name_ml": full_name_ml,
#         "spouse_ml": spouse_name_ml,
#         "children": []
#     }

#     children = Person.objects.filter(family_groups=family_group).filter(
#         father=person) | Person.objects.filter(family_groups=family_group).filter(mother=person)

#     for child in children.distinct():
#         child_name_en = f"{child.first_name} {child.last_name}"
#         child_spouse_en = f"({child.spouse.first_name} {child.spouse.last_name})" if child.spouse else ""
#         child_name_ml = translate_to_malayalam(child_name_en)
#         child_spouse_ml = translate_to_malayalam(child.spouse.first_name + " " + child.spouse.last_name) if child.spouse else ""

#         tree["children"].append({
#             "id": child.id,
#             "name_en": child_name_en,
#             "spouse_en": child_spouse_en,
#             "name_ml": child_name_ml,
#             "spouse_ml": child_spouse_ml,
#             "children": []
#         })

#     return tree



@login_required
def family_tree_dynamic_view(request):
    try:
        family_group = FamilyGroup.objects.get(staff_user=request.user)
        root_person = Person.objects.filter(family_groups=family_group, father__isnull=True, mother__isnull=True).first()
        if not root_person:
            return JsonResponse({"error": "No root person found."}, status=400)

        tree_data = build_two_level_tree(root_person, family_group)
    except FamilyGroup.DoesNotExist:
        return JsonResponse({"error": "Family not found"}, status=404)

    return render(request, 'family_tree_dynamic.html', {'tree_data': tree_data})


@login_required
def fetch_person_tree(request, person_id):
    try:
        person = get_object_or_404(Person, id=person_id)
        family_group = FamilyGroup.objects.get(staff_user=request.user)
        tree = build_two_level_tree(person, family_group)
        return JsonResponse(tree, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def family_tree_dynamic_view_old(request):
    """Load only the root person for the user's assigned family group"""
    try:
        family_group = FamilyGroup.objects.get(staff_user=request.user)
        
        # Get the root ancestor(s) (person without a father & mother in this group)
        root_persons = Person.objects.filter(family_groups=family_group, father__isnull=True, mother__isnull=True).values(
            "id", "first_name", "gender", "photo"
        )
        print(root_persons)
        tree_data = list(root_persons)  # Convert QuerySet to a list for JSON
    except FamilyGroup.DoesNotExist:
        tree_data = []  # No family assigned to the user

    return render(request, "family_tree_dynamic.html", {"tree_data": json.dumps(tree_data)})


@login_required
def get_children_old(request, person_id):
    """Fetch child nodes dynamically when clicking a node"""
    try:
        # Ensure the person belongs to the logged-in user's family group
        person = get_object_or_404(Person, id=person_id, family_groups__staff_user=request.user)
        
        # Get the person's children
        children = person.children.all().values("id", "name", "gender", "photo")
        
        return JsonResponse(list(children), safe=False)
    except Person.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
def family_tree_view(request):
    

    try:
        
        family_group = FamilyGroup.objects.get(staff_user=request.user)
        
        root_person = Person.objects.filter(family_groups=family_group, father__isnull=True, mother__isnull=True).first()
        
        if not root_person:
            return JsonResponse({"error": "No root person found for this family"}, status=400)

        # Build the JSON hierarchy for the assigned family group
        tree_data = build_family_tree(root_person, family_group)
        print(tree_data)
    except FamilyGroup.DoesNotExist:
        print("Error")
        tree_data = []  # No family assigned to the user

    
    return render(request, 'family_tree.html', {'tree_data': json.dumps(tree_data)})

def build_family_tree_old(person, family_group):
    """Build the family tree recursively in a format compatible with D3.js, including the spouse's name."""
    
    # Get spouse name (if exists)
    spouse = f" ({person.spouse.first_name} {person.spouse.last_name})" if person.spouse else ""

    tree = {
        'name': f"{person.first_name} {person.last_name}{spouse}",  # Include spouse in brackets
        'children': []
    }

    children = Person.objects.filter(father=person, family_groups=family_group) | Person.objects.filter(mother=person, family_groups=family_group)
    
    for child in children:
        tree['children'].append(build_family_tree(child, family_group))

    return tree

@login_required
def person_detail(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    return render(request, 'person_detail.html', {'person': person})

@login_required
def export_family_tree_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="family_tree.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'First Name', 'Last Name', 'Father ID', 'Mother ID', 'Spouse ID'])
    for person in Person.objects.all():
        writer.writerow([person.id, person.first_name, person.last_name, person.father_id, person.mother_id, person.spouse_id])
    return response

@login_required
def export_family_tree_json(request):
    print("Hi")
    data = [person.get_family_tree() for person in Person.objects.all()]
    return JsonResponse({'family_tree': data}, safe=False)

@login_required
def export_family_tree_pdf(request):
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="family_tree.pdf"'
    # pdf = canvas.Canvas(response, pagesize=landscape(letter))
    # pdf.setFont("Helvetica", 10)
    # y_position = 550
    # pdf.drawString(50, y_position, "Family Tree")
    # y_position -= 20
    # for person in Person.objects.all():
    #     pdf.drawString(50, y_position, f"{person.first_name} {person.last_name} (ID: {person.id})")
    #     y_position -= 15
    # pdf.save()
    # return response

    # Prepare the HTTP response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="family_tree.pdf"'
    
    # Create a canvas to generate the PDF
    c = canvas.Canvas(response, pagesize=letter)
    
    # Define starting positions for the family tree drawing
    x_offset = 200
    y_offset = 750  # Start near the top of the page
    
    # Function to draw family tree recursively
    def draw_family_tree(c, person, x, y, level=0, max_levels=5, sibling_gap=70, child_gap=75):
        """
        Recursively draws family tree, positioning family members with respect to each other.
        - x, y: The starting coordinates for the person on the canvas.
        - level: The current level in the family tree (0 is the root).
        - max_levels: Limits how many levels of the tree to print.
        - sibling_gap: Distance between siblings (children of the same parent).
        - child_gap: Distance between generations (vertical space between parent and children).
        """
        # Base condition to stop recursion if maximum levels are reached
        if level >= max_levels:
            return y
        
        # Draw the name of the person
        c.setFont("Helvetica", 10)
        c.drawString(x, y, f"{person.first_name} {person.last_name}")
        
        # Find children of the current person (those who have this person as their parent)
        children = Person.objects.filter(father=person) | Person.objects.filter(mother=person)
        
        if children.exists():
            # Draw lines to children and recursively draw them
            child_y_offset = y - child_gap  # Space below parent for children
            for idx, child in enumerate(children):
                child_x = x + (idx - len(children) / 2) * sibling_gap  # Distribute children horizontally
                c.setStrokeColor(colors.black)
                c.setLineWidth(1)
                c.line(x, y - 10, child_x, child_y_offset + 10)  # Line from parent to child
                # Recursive call for each child (draw them in the next level)
                child_y_offset = draw_family_tree(c, child, child_x, child_y_offset, level + 1)
        
        return y - len(children) * child_gap  # Return the updated y-position after drawing children
    
    # Get the starting point (usually the oldest family member or root person)
    root_person = Person.objects.filter(father__isnull=True, mother__isnull=True).first()
    
    if root_person:
        # Draw the family tree starting from the root person
        draw_family_tree(c, root_person, x_offset, y_offset)
    
    # Save the PDF
    c.showPage()
    c.save()
    return response

@login_required
def family_tree_page(request):
    return HttpResponse(FAMILY_TREE_HTML)

@login_required
def person_detail_page(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    return HttpResponse(PERSON_DETAIL_HTML.replace("{{ person.first_name }}", person.first_name).replace("{{ person.last_name }}", person.last_name).replace("{{ person.birth_date }}", str(person.birth_date) if person.birth_date else "N/A").replace("{{ person.death_date }}", str(person.death_date) if person.death_date else "N/A").replace("{{ person.gender }}", person.gender).replace("{{ person.photo.url }}", person.photo.url if person.photo else "").replace("{{ person.father }}", person.father.first_name if person.father else "N/A").replace("{{ person.mother }}", person.mother.first_name if person.mother else "N/A").replace("{{ person.spouse }}", person.spouse.first_name if person.spouse else "N/A"))

import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Person, FamilyGroup

@login_required
def import_csv_old(request):
    """View to handle CSV file upload and import Person data"""
    
    if request.method == "POST":
        print("POST")
        csv_file = request.FILES.get("csv_file")
        print(csv_file)
        if not csv_file:
            print("Error")
            messages.error(request, "No file uploaded.")
            return redirect("dashboard")

        try:
            print("1")
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            print("2")
            count = 0
            for row in reader:
                # print(row)
                # Ensure mandatory fields exist
                first_name = row.get("First Name", "").strip()
                last_name = row.get("Last Name", "").strip()
                gender = row.get("Gender", "").strip().upper()
                birth_date = row.get("Birth Date", None)
                death_date = row.get("Death Date", None)
                father_name = row.get("Father", "").strip()
                mother_name = row.get("Mother", "").strip()
                spouse_name = row.get("Spouse", "").strip()
                family_group_name = row.get("Family Group", "").strip()
                # print(family_group_name)
                # print(first_name)
                if not first_name and not last_name:
                    count+=1
                    print(count)
                    continue  # Skip rows with missing required fields

                # Get or create Family Group
                family_group, _ = FamilyGroup.objects.get_or_create(name=family_group_name)
                # print(family_group)
                # Fetch or create person
                person, _ = Person.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={
                        "gender": gender,
                        "birth_date": birth_date or None,
                        "death_date": death_date or None,
                    }
                )

                # Assign to family group
                person.family_groups.add(family_group)

                # Assign father
                if father_name:
                    # father = Person.objects.filter(first_name=father_name.split()[0], last_name=father_name.split()[-1]).first()
                    father = Person.objects.filter(first_name=father_name).first()
                    print(father)
                    if father:
                        person.father = father

                # Assign mother
                if mother_name:
                    
                    # mother = Person.objects.filter(first_name=mother_name.split()[0], last_name=mother_name.split()[-1]).first()
                    mother = Person.objects.filter(first_name=mother_name).first()
                    print(mother)
                    if mother:
                        person.mother = mother

                # Assign spouse
                if spouse_name:
                    # spouse = Person.objects.filter(first_name=spouse_name.split()[0], last_name=spouse_name.split()[-1]).first()
                    spouse = Person.objects.filter(first_name=spouse_name).first()
                    
                    if spouse:
                        person.spouse = spouse
                
                print(person)

                # Save the person record
                person.save()

            messages.success(request, "CSV file imported successfully!")
            return redirect("dashboard")

        except Exception as e:
            print(e)
            print("Error file")
            messages.error(request, f"Error processing file: {str(e)}")
            return redirect("dashboard")

    return render(request, "import_csv.html")


def import_csv(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.error(request, "No file uploaded.")
            return redirect("dashboard")

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            count = 0

            for row in reader:
                first_name = row.get("First Name", "").strip()
                last_name = row.get("Last Name", "").strip()
                gender = row.get("Gender", "").strip().upper()
                birth_date = row.get("Birth Date", None)
                death_date = row.get("Death Date", None)
                father_name = row.get("Father", "").strip()
                mother_name = row.get("Mother", "").strip()
                spouse_name = row.get("Spouse", "").strip()
                family_group_name = row.get("Family Group", "").strip()

                if not first_name and not last_name:
                    continue

                family_group, _ = FamilyGroup.objects.get_or_create(name=family_group_name)

                # Check if person already exists in the family group
                existing_persons = Person.objects.filter(first_name=first_name, family_groups=family_group)
                if existing_persons.exists():
                    person = existing_persons.first()
                    updated = False
                else:
                    person = Person(
                        first_name=first_name,
                        last_name=last_name,
                        gender=gender,
                        birth_date=birth_date or None,
                        death_date=death_date or None,
                    )
                    person.save()
                    person.family_groups.add(family_group)
                    updated = True

                # Update father
                if father_name and not person.father:
                    father = Person.objects.filter(first_name=father_name, family_groups=family_group).first()
                    if father:
                        person.father = father
                        updated = True

                # Update mother
                if mother_name and not person.mother:
                    mother = Person.objects.filter(first_name=mother_name, family_groups=family_group).first()
                    if mother:
                        person.mother = mother
                        updated = True

                # Update spouse
                if spouse_name and not person.spouse:
                    spouse = Person.objects.filter(first_name=spouse_name, family_groups=family_group).first()
                    if spouse:
                        person.spouse = spouse
                        updated = True

                if updated:
                    person.save()

            messages.success(request, "CSV file imported successfully!")
            return redirect("dashboard")

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            return redirect("dashboard")

    return render(request, "import_csv.html")
