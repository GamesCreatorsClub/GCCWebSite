import os
import re
import shutil
import html

destination = "posts/old"
picturesDestination = "images/old"
source = "old-website"

def stripSrc(s):
    if s.startswith("src=\""):
        return s[5:len(s)-1]
    return s


def extractTag(name):
    tag = ""
    i = 0
    while i < len(name) and not name[i].isdigit():
        i = i + 1

    return name[0:i]


def copyPictures(dir, srcs):
    for src in srcs:
        if not src.endswith("html") and not src.startswith("data:"):
            src = html.unescape(src)
            src = src.replace("%20", " ")
            if src.startswith(dir + "_files"):
                fullName = source + "/" + src
                src = src[len(dir + "_files") + 1:]
            else:
                fullName = source + "/" + dir + "_files/" + src
            if os.path.exists(fullName):
                shutil.copyfile(fullName, picturesDestination + "/" + src)


def process(text, tags, dir):
    header = tags
    text = text.replace("https://web.archive.org/web/20170315220529/", "")

    lines = text.split("\n")
    i = 0
    while i < len(lines) and not "<h2>" in lines[i]:
        if lines[i].startswith(".. "):
            header.append(lines[i])
            del lines[i]
            i = i - 1
        i = i + 1

    if i < len(lines):
        i = i - 1
        while i > -1:
            del lines[i]
            i = i - 1

    inh2 = False
    i = 0
    while i < len(lines) and not "</dl>" in lines[i]:
        if "<h2>" in lines[i]:
            inh2 = True
        elif "</h2>" in lines[i]:
            inh2 = False
        elif "</a>" in lines[i] and inh2:
            title = lines[i].replace("</a>", "").strip()
            header.append(".. title: " + title)
        elif "<dl" in lines[i]:
            del lines[i]
            i = i - 1
        elif "<dt" in lines[i]:
            del lines[i]
            i = i - 1
        elif "</dt>" in lines[i]:
            del lines[i]
            i = i - 1
        elif "<dd class=\"published\">" in lines[i]:
            del lines[i]
            p = lines[i]
            del lines[i]
            p = p.replace("</dd>", "").strip().split(",")[1].strip()
            header.append(".. date: " + p)
            i = i - 1
        elif "<dd class=\"createdby\">" in lines[i]:
            del lines[i]
            del lines[i]
            c = lines[i]
            del lines[i]
            c = c.replace("</dd>", "").strip()
            if c.startswith("Written by "):
                c = c[11:]
            header.append(".. author: " + c)
            i = i - 1
        elif "<dd class=\"hits\">" in lines[i]:
            del lines[i]
            del lines[i]
            i = i - 1

        i = i + 1

    if i < len(lines):
        if "</dl>" in lines[i]:
            del lines[i]

    text = "\n".join(header) + "\n\n" + "\n".join(lines) + "\n"

    text = text.replace("src=\"" + dir + "_files/", "src=\"")

    srcs = re.findall("src=\"[^\"]+\"", text)

    srcs = list(map(stripSrc, srcs))

    copyPictures(dir, srcs)

    text = text.replace("src=\"", "src=\"../../../" + picturesDestination + "/")

    text = text.replace("src=\"../../../" + picturesDestination + "/" + dir, "src=\"../../../" + picturesDestination)
    text = text.replace("src=\"../../../" + picturesDestination + "/" + html.escape(dir.replace(" ", "%20")) + "_files/", "src=\"../../../" + picturesDestination + "/")

    text = text.replace("src=\"../../../" + picturesDestination + "/data:image", "src=\"data:image")

    return text


files = os.listdir(source)
for file in files:
    if file.endswith(".html"):
        dir = file[0 : len(file) - 5]
        print("Processing " + file)

        tag = extractTag(file)

        with open(source + "/" + file, "r") as file:
            text = file.read()
            # text = text.split("<div class=\"blog\">")[1]

            text = text.replace("items-leading\">", "item-separator\"></div>")
            arcticles = text.split("<div class=\"item-separator\"></div>")
            del arcticles[len(arcticles) - 1]
            for arcticle in arcticles:
                name = arcticle.split("http://raspberrypilot.com/")[1].split("\">")[0]
                n = name.split("/")
                name = name.split("/")[len(n) - 1]

                print("  Testing " + name)
                if not name.startswith("html;"):
                    print("  Writting " + name)
                    arcticle = process(arcticle, [".. tags: " + tag, ".. slug: " + name], dir)

                    filename = destination + "/" + name + ".html"
                    # os.mkdirs("output")
                    with open(filename, "w") as f:
                        f.write(arcticle)
                        f.close


# files = os.listdir(destination)
# for file in files:
#     if file.endswith(".html"):
#         print("Processing " + file + "...")
#         with open(destination + "/" + file, "r") as f:
#             header = []
#             text = f.read()
#
#             header = []
#             text = text.replace("https://web.archive.org/web/20170315220529/", "")
#
#             lines = text.split("\n")
#             i = 0
#             while i < len(lines) and not "<h2>" in lines[i]:
#                 if lines[i].startswith(".. "):
#                     header.append(lines[i])
#                     del lines[i]
#                     i = i - 1
#                 i = i + 1
#
#             if i < len(lines):
#                 i = i - 1
#                 while i > -1:
#                     del lines[i]
#                     i = i - 1
#
#             inh2 = False
#             i = 0
#             while i < len(lines) and not "</dl>" in lines[i]:
#                 if "<h2>" in lines[i]:
#                     inh2 = True
#                 elif "</h2>" in lines[i]:
#                     inh2 = False
#                 elif "</a>" in lines[i] and inh2:
#                     title = lines[i].replace("</a>", "").strip()
#                     header.append(".. title: " + title)
#                 elif "<dl" in lines[i]:
#                     del lines[i]
#                     i = i - 1
#                 elif "<dt" in lines[i]:
#                     del lines[i]
#                     i = i - 1
#                 elif "</dt>" in lines[i]:
#                     del lines[i]
#                     i = i - 1
#                 elif "<dd class=\"published\">" in lines[i]:
#                     del lines[i]
#                     p = lines[i]
#                     del lines[i]
#                     p = p.replace("</dd>", "").strip().split(",")[1].strip()
#                     header.append(".. date: " + p)
#                     i = i - 1
#                 elif "<dd class=\"createdby\">" in lines[i]:
#                     del lines[i]
#                     del lines[i]
#                     c = lines[i]
#                     del lines[i]
#                     c = c.replace("</dd>", "").strip()
#                     if c.startswith("Written by "):
#                         c = c[11:]
#                     header.append(".. author: " + c)
#                     i = i - 1
#                 elif "<dd class=\"hits\">" in lines[i]:
#                     del lines[i]
#                     del lines[i]
#                     i = i - 1
#
#                 i = i + 1
#
#             if i < len(lines):
#                 if "</dl>" in lines[i]:
#                     del lines[i]
#
#             text = "\n".join(header) + "\n\n" + "\n".join(lines) + "\n"
#
#             with open(destination + "/" + file, "w") as fi:
#                 fi.write(text)
#                 fi.close()
#         print("Processed " + file + ".")


