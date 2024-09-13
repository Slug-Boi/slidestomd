# slidestomd (slides to markdown)
A cli for converting PDFs into a markdown file of images with headers

# Requirements
- Python 3 (with pip)
- pdftoppm (or any other pdf to image converter)

Run the following to install the required python packages
```
$ pip install -r requirements.txt
```

# Usage
<...>: Required args  
[...]: Optional args
  
Currently you have to run the pdf to image cli yourself. I recommend pdftoppm. (this might be added to the python script later)

After the pdf is converted to a folder of images with the format NAME-xx.png (xx being a number) one can run the program using 
```
$ python slidetomd.py <folder_of_images> <name_of_md_file> [pixel_spacing]
```
`pixel_spacing` is the accepted amount of distance between words based on their y values. This will determine if words are on the same line. This should ideally be as low as possible but might break if its too low. Default is 7
