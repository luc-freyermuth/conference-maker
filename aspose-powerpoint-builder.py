import aspose.slides as slides


with slides.Presentation("Base.pptx") as pres1:
    with slides.Presentation("GP_1.pptx") as pres2:
        for slide in pres2.slides:
            print('adding slides')
            pres1.slides.add_clone(slide)
    with slides.Presentation("EE_2.pptx") as pres2:
        for slide in pres2.slides:
            print('adding slides 2')
            pres1.slides.add_clone(slide)
    pres1.save("presentation_1.pptx", slides.export.SaveFormat.PPTX)