from storm.locals import *

class _FileTag(object):
    __storm_table__ = "SyncedFileTag"
    __storm_primary__ = "fileID", "tag"

    STATUS_NEW = 0
    STATUS_SYNCED = 1
    STATUS_DELETED = 2

    fileID = Int()
    tag = Unicode()
    status = Int()

    def __init__(self, tag_name):
        self.tag = tag_name
        self.status = _FileTag.STATUS_NEW

class FileInfo(object):
    __storm_table__ = "SyncedFile"

    ID = Int(primary = True)
    fileURI = Unicode()
    __tags = ReferenceSet(ID, _FileTag.fileID)

    def __init__(self, uri, temp_store):
        self.fileURI = uri
        self.__temp_store = temp_store

    def tag(self, tag_name, local):
        tag_name = unicode(tag_name)
        store = Store.of(self)
        if store == None:
            # First tag
            tag = _FileTag(tag_name)
            self.__tags.add(tag)
            self.__temp_store.add(self)
            return True
        else:
            current_tag = store.find(_FileTag, fileID = self.ID, tag = tag_name).one()
            if current_tag:
                if current_tag.status == _FileTag.STATUS_DELETED:
                    current_tag.status = _FileTag.STATUS_SYNCED
                    current_tag.flush()
                    return True
                else:
                    return False
            else:
                tag = _FileTag(tag_name)
                self.__tags.add(tag)
                return True
    
    def untag(self, tag_name):
        tag_name = unicode(tag_name)
        store = Store.of(self)
        current_tag = store.find(_FileTag, fileID = self.ID, tag = tag_name).one()
        if not current_tag:
            return
        if current_tag.status == _FileTag.STATUS_NEW:
           store.remove(current_tag)

    def tags(self):
        if Store.of(self) == None:
            return []
        return [tag.tag for tag in self.__tags if tag.status != _FileTag.STATUS_DELETED]
    
    def __get_store(self):
        store = Store.of(self)
        return store if store else self.__temp_store
