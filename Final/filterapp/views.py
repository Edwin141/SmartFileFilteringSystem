import string
import docx
import os
import pytesseract
import PIL.Image
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

from pdf2image import convert_from_path
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import FileInfo
from django.conf import settings
from django.templatetags.static import static
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .forms import CustomUserCreationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView


myconfig = r"--psm 11  --oem 3"  # Tesseract configuration options

def process_image(image):
    text = pytesseract.image_to_string(image, config=myconfig)
    return text

def process_pdf(pdf_file):
    images = convert_from_path(pdf_file)
    text = ""
    for image in images:
        text += process_image(image)
    return text

@login_required         # UNCOMMENT THIS TO FORCE USER TO LOGIN IN ORDER TO VIEW HOME PAGE
def home(request): 
    return render(request, 'home.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = AuthenticationForm

    def get_context_data(self, **kwargs):
            context = super(CustomLoginView, self).get_context_data(**kwargs) # Update this line
            context['view'] = 'login'
            return context



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def preprocess_text(text):
    # Lowercase the text
    text = text.lower()
    
    # Remove punctuations
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenize the text
    words = word_tokenize(text)

    # Remove stopwords
    words = [word for word in words if word not in stopwords.words('english')]

    # Lemmatize the words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # Join the words back into a single string
    text = ' '.join(words)

    return text




def get_cosine_similarity(query, documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix)
    return cosine_similarities


def search(request):
    query = request.GET.get('q', '')
    if query:
        files = FileInfo.objects.all()
        documents = [file.content for file in files]
         # Preprocess the query text
        preprocessed_query = preprocess_text(query)
        
        cosine_similarities = get_cosine_similarity(preprocessed_query, documents)
        top_indices = cosine_similarities.argsort().flatten()[-3:][::-1]  #To change the amount of search results
        results = [files[int(i)] for i in top_indices]
        return render(request, 'home.html', {'results': results})
    else:
        return render(request, 'home.html', {'results': []})

def upload_files_page(request):
    return render(request, 'upload.html')

def process_docx(docx_file):
    doc = docx.Document(docx_file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)

@csrf_exempt
def upload_files(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('file')
        for file in uploaded_files:
            file_path = os.path.join(settings.BASE_DIR, 'static', 'StoredFiles', file.name)
            text_file_path = os.path.splitext(file_path)[0] + ".txt"
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            ext = os.path.splitext(file.name)[1].lower()
            if ext == '.pdf':
                text_content = process_pdf(file_path)
            elif ext in ['.jpg', '.jpeg', '.png']:
                image = PIL.Image.open(file_path)
                text_content = process_image(image)
            elif ext == '.txt':
                with open(file_path, 'r') as file:
                    text_content = file.read()
            elif ext == '.docx':
                text_content = process_docx(file_path)
            with open(text_file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text_content)

                # Save file information in the database
                file_info = FileInfo(
                    filename=os.path.basename(file.name),
                    content=text_content,
                    file_type=ext,
                    tags="",  
                    file_path=os.path.join('static', 'StoredFiles', os.path.basename(text_file_path))
                )
                file_info.save()

        return JsonResponse({'status': 'success'})
    else:  
        return JsonResponse({'status': 'error'}) 
    

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form, 'view': 'register'})



def logout_view(request):
    logout(request)
    return redirect('login')

