import os.path
from django.db import models

class RenameFilesModel(models.Model):
    """
    Abstract model implementing a two-phase save in order to rename
    `FileField` and `ImageField` filenames after saving.  This allows the
    final filenames to contain information like the primary key of the model.
    
    Example:
    
        class Photo(RenameFilesModel):
            file = models.ImageField(upload_to='uploads/temp')
            
            RENAME_FILES = {
                'file': {'dest': 'uploads/photos/photo.jpg'}
            }
        
        >>> photo = Photo(file='uploads/temp/photo.jpg')
        >>> photo.pk
        
        >>> photo.save()
        >>> photo.pk
        1
        >>> photo.file
        <ImageFieldFile: uploads/photos/1/photo.jpg>
    
    If the 'dest' option is a callable, it will be called with the model
    instance (guaranteed to be saved) and the currently saved filename, and
    must return the new filename.  Otherwise, the filename is determined by
    'dest' and the model's primary key.
    
    If a file already exists at the resulting path, it is deleted.  This is
    desirable if the filename should always be the primary key, for instance.
    To avoid this behavior, write a 'dest' handler that results in a unique
    filename.
        
    
    """
    RENAME_FILES = {}
    
    class Meta:
        abstract = True
    
    def save(self, force_insert=False, force_update=False,*args, **kwargs):
        rename_files = getattr(self, 'RENAME_FILES', None)
        if rename_files:
            super(RenameFilesModel, self).save(force_insert, force_update)
            force_insert, force_update = False, True
            
            for field_name, options in iter(rename_files.items()):
                field = getattr(self, field_name)
                if field.name:
                    file_name = field.name
                    name=os.path.basename(file_name)
                    final_dest = options['dest']
                    if callable(final_dest):
                        final_name = final_dest(self, name)
                    else:
                        final_name = os.path.join(final_dest, '%s' % (self.pk,),name)
                    if name and file_name != final_name:
                        field.storage.delete(final_name)
                        field.storage.save(final_name, field)
                        field.close()
                        field.storage.delete(file_name)
                        setattr(self, field_name, final_name)
        
        super(RenameFilesModel, self).save(force_insert, force_update)