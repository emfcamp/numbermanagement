from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AudioFile
from .forms import AudioFileForm

@login_required
def audio_list(request):
    audio_files = AudioFile.objects.filter(user=request.user)
    return render(request, 'audio_manager/audio_list.html', {'audio_files': audio_files})

@login_required
def upload_audio(request):
    if request.method == 'POST':
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.save(commit=False)
            audio.user = request.user
            audio.save()
            messages.success(request, 'Audio file uploaded successfully!')
            return redirect('audio_list')
        else:
            messages.error(request, 'Error uploading file. Please check the file size and format.')
    else:
        form = AudioFileForm()
    return render(request, 'audio_manager/upload_audio.html', {'form': form})

@login_required
def delete_audio(request, pk):
    audio = get_object_or_404(AudioFile, pk=pk, user=request.user)
    if request.method == 'POST':
        audio.delete()
        messages.success(request, 'Audio file deleted successfully!')
        return redirect('audio_list')
    return render(request, 'audio_manager/confirm_delete.html', {'audio': audio})