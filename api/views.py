from django.http import HttpResponse
from reportlab.pdfgen import canvas
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import pandas as pd
from .models import EquipmentData

class UploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        # 1. Get the file from the request
        file_obj = request.FILES['file']
        
        # 2. Save file to database
        instance = EquipmentData.objects.create(file=file_obj)
        
        # 3. Read the file using Pandas
        try:
            df = pd.read_csv(instance.file.path)
            
            # 4. Calculate Stats
            stats = {
                "total_count": int(len(df)),
                "avg_flowrate": float(df['Flowrate'].mean()) if 'Flowrate' in df else 0,
                "avg_pressure": float(df['Pressure'].mean()) if 'Pressure' in df else 0,
                "avg_temp": float(df['Temperature'].mean()) if 'Temperature' in df else 0,
                "type_distribution": df['Type'].value_counts().to_dict() if 'Type' in df else {}
            }
            
            # 5. Return data to frontend
            return Response({
                "stats": stats, 
                "data": df.head(50).to_dict(orient='records') # Send first 50 rows
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)

def generate_pdf(request):
    # 1. Get the last uploaded file
    last_entry = EquipmentData.objects.last()

    if not last_entry:
        return HttpResponse("No data uploaded yet.", status=404)

    # 2. Calculate Stats again (or fetch from DB if optimized)
    df = pd.read_csv(last_entry.file.path)
    avg_pressure = df['Pressure'].mean()
    avg_temp = df['Temperature'].mean()
    total_count = len(df)

    # 3. Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 800, "Chemical Equipment Analysis Report")

    # Stats
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"File Analyzed: {last_entry.file.name}")
    p.drawString(100, 730, f"Total Equipment Count: {total_count}")
    p.drawString(100, 710, f"Average Pressure: {avg_pressure:.2f} Pa")
    p.drawString(100, 690, f"Average Temperature: {avg_temp:.2f} C")

    p.drawString(100, 650, "Generated automatically by Django Backend.")

    p.showPage()
    p.save()

    # 4. Return PDF as response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response