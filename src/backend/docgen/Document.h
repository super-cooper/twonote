#include <string>
#include <bits/unique_ptr.h>

namespace html {

/**
 * This class represents a standard HTML document that we will use to render a page of a notebook
 */
class Document {
private:
    // buffer used for holding the raw HTML code
    std::string doc_buffer;
    // filesystem path where this document is stored on disk
    std::string path;

public:

    /**
     * Returns the buffer for this document
     * @return An r-value of this->doc_buffer
     */
    std::string &&get_buffer();

    /**
     * Returns the path in the filesystem of this document
     * @return
     */
    std::string &&get_path();

    /**
     * Gets the character at a particular location in the buffer
     * @param index
     * @return
     */
    char operator[](int index);

};

}