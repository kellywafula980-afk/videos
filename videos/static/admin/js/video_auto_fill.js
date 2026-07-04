document.addEventListener('DOMContentLoaded', function() {
    // Find the file input field for 'video_file'
    const fileInput = document.querySelector('#id_video_file');
    // Find the Title and Description input fields
    const titleInput = document.querySelector('#id_title');
    const descInput = document.querySelector('#id_description');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const file = e.target.files[0];
                
                // 1. Extract the filename and remove the extension
                let rawName = file.name;
                let cleanName = rawName.substring(0, rawName.lastIndexOf('.')) || rawName;
                
                // 2. Clean up dashes and underscores for a better looking title
                cleanName = cleanName.replace(/[_-]/g, ' ');
                
                // 3. Auto-fill Title if it's currently empty
                if (titleInput && !titleInput.value) {
                    titleInput.value = cleanName;
                }
                
                // 4. Auto-fill Description if it's currently empty
                if (descInput && !descInput.value) {
                    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
                    descInput.value = `Uploaded video file: ${rawName} (${fileSizeMB} MB).`;
                }
            }
        });
    }
});
