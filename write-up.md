Plan for now:
    Encoding:
        Takes in a video and parameter for rounding colors (None, Low, Medium, High)
            None - keeps colors as are
            Low - rounds to nearest multiple of 5
            Medium - rounds to nearest multiple of 50
            High - black and white
        Get frames and fps
        Get size of frame
        Get pixels
        Determine color-->pixel encoding to use based on rounding parameter
        Initialize DNA
        Write fps to DNA
        Write frame size to DNA
        Write out first frame's pixels to DNA
        For each frame, for each pixel
            if same as previous, write G to DNA
            else write C, then new colors to DNA
        return DNA
    Decoding:
        Takes in DNA, rounding parameter (to know how to decode), and "mutation" (recessive, sickle, cancer, RIP,  ...)
            Recessive - 25% chance for previous pixel to remain
            Sickle - GAG --> GTG, CTC --> CAC https://pmc.ncbi.nlm.nih.gov/articles/PMC7510211/
            Cancer - 10% chance for pixels next to starting empty pixel to become empty as well
            RIP - C --> T when a pixel is the same as the previous one https://pmc.ncbi.nlm.nih.gov/articles/PMC1451165/
            ...
        Get fps and frame size (m, n)
        for every m * n pixels:
            initialize image with frame size
            decode each pixel in each frame
            write pixel to image
        concat images to video with same fps
        return video
    
    Analysis
        compare storage size of original video vs. DNA encoding with different rounding color values
        see how each mutation affects the video
        check how long the encoding and deoding take

