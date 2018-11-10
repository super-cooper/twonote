#include "Document.h"

namespace html {


std::string &&Document::get_buffer() {
    return std::move(doc_buffer);
}

std::string &&Document::get_path() {
    return std::move(path);
}

char Document::operator[](int index) {
    return doc_buffer[index];
}
}
