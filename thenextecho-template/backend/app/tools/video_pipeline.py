import logging
from app.models.job import JobStatus

async def run_pipeline_step(current_status, theme, artifacts):
    logging.info(f"Exécution du pipeline pour le thème '{theme}' à l'étape '{current_status}'")
    
    if current_status in [JobStatus.PENDING, JobStatus.AWAITING_SCRIPT_APPROVAL]:
        # Logique pour (re)générer le script
        script_text = f"Ceci est un script génial sur {theme}. C'est une nouvelle version."
        return JobStatus.AWAITING_SCRIPT_APPROVAL, {"script": script_text}, None
        
    elif current_status == JobStatus.SCRIPT_APPROVED:
        # Logique pour générer l'audio
        audio_path = f"/path/to/audio_for_{theme.replace(' ', '_')}.mp3"
        return JobStatus.AWAITING_AUDIO_APPROVAL, {"audio_path": audio_path}, None
        
    elif current_status == JobStatus.AUDIO_APPROVED:
        # Logique pour chercher les images
        images = ["/img1.jpg", "/img2.jpg"]
        return JobStatus.COMPILING, {"image_paths": images}, None
        
    elif current_status == JobStatus.COMPILING:
        # Logique pour compiler la vidéo
        video_path = f"/videos/{theme.replace(' ', '_')}.mp4"
        return JobStatus.COMPLETED, {"final_video_path": video_path}, None
    
    return current_status, None, "Étape inconnue ou finale"
