# June Moretz Engineering Notebook - avspl1t (CS2620 Final Project)

A high-level note: this engineering notebook mostly includes general project motivations and notes throughout time on work performed and lessons learned. The fine-grained details of how the system works, as well as a lot of the explanation for why those choices were made, can be found in the other documents in the docs folder. These documents should be read as part of this engineering notebook, with this document alone as more of a supplement!

## April 8, 2025

This project--building a distributed video encoding system--is one that has been on my mind for a long time (since around 2020), but not one I have ever had the time or a sufficiently good reason to take on. Thus, I'm approaching this having already thought in some amount of detail about the architecture for a system like this. I've also worked with HLS video encoding in the past for another project, though only on a single machine. I have not worked with AV1 before.

While I'm only starting to write this today, many of the thoughts here have already been under consideration within my head for the last few weeks or longer, though never put on paper. I'm writing them down both here and in the docs folder, in a somewhat significant level of detail, largely in the hope of creating a sufficient amount of system-level documentation that Catherine and I can refine the design and architecture and that she can begin work on whatever parts of the system she ultimately ends up taking on. (From our preliminary conversations, this will likely at least include the coordinator server. I plan to take more of a lead on the system design, protocol design, and the client, as well as possibly the worker.)

### The Problem

Video encoding requires high amounts of computational power. Modern video codecs allow extremely good lossy compression, taking the enormous amount of data in an uncompressed video file and transforming it into a far smaller file without a significant drop in perceived quality. As advancements in video compression technology have taken place, they have allowed video files to become smaller and smaller while retaining the same perceptual quality.

However, these smaller files are not without a cost. Better video codecs require more computational power both for encoding and decoding. In some cases, this can be augmented by specialized hardware (most computers today have hardware decoding support for common video codecs, and hardware encoders exist too), but in others, particularly on the encoding side, the only solution is more compute power.

Encoding is generally far more computationally intensive than decoding. Despite this computational cost, it can make sense to encode videos into new codecs, like the open-source AV1 codec. These modern codecs decrease file size, and for a video that will be watched thousands or millions of times, the decrease in bandwidth usage makes up for the increase in encoding time. Large video distributors like YouTube and Netflix are thus significant adapters of new codecs like AV1, expending the upfront effort to produce a smaller file without losing quality so as to minimize bandwidth usage for streaming once that file has been produced.

Computational power, though, isn’t the only problem. Video encoders are built to run on a single computer. While YouTube may be large enough to dedicate thousands of computers to encoding videos into AV1, each of those computers can only encode one video at a time, and each video can only be assigned to one computer. This creates a latency bottleneck. When trying to encode a large file into AV1, it can take hours or days for that encoded video to be produced. A simple solution of adding more computers allows simultaneously encoding more videos, but does not solve this latency problem.

### The Goal

Build a system that uses the power of distributed systems to encode a single video across multiple computers, decreasing the time from starting an encode to having a finished encode, particularly for computationally complex codecs like AV1.

### Our Solution

We intend to build avspl1t, a system for distributed parallel video encoding. This system will split a single video file into smaller pieces, each only a few seconds long. Those individual pieces can then be split among worker machines, each of which will encode one piece at a time. By splitting a single video encoding job across a network of machines, the time between starting and finishing an encode can be dramatically reduced, and adding more computational power can decrease both latency and throughput. This enhances the utility of modern codecs like AV1, making them usable in more situations.

Furthermore, we intend to use the HLS format for outputting encoded videos. HLS works by splitting a single video stream into a number of separate pieces, which are then downloaded and reassembled into a constant stream of video by the client. HLS is a natural fit for distributed video encoding, as it has benefits for clients (like allowing adaptive bitrate streaming, i.e., switching between different qualities of video dynamically based on network conditions) and for our server, removing the need for a merge step. Since each encoded video piece can be treated directly as an HLS fragment, the system only needs to create an HLS manifest file - the fragmented outputs of the workers can be used directly as the encoded video output.

In sum, our system should take an input video file, split it into segments, encode those segments in parallel, and output an AV1-encoded HLS stream.

We will be building a complete software system, and will thus be submitting our code, documentation, and engineering notebooks (as well as our project presentation/demo video). As video encoding is necessarily time consuming, we intend to present our system by showing a recorded demonstration video showcasing how it can be used and demonstrating its ability to transcode segments of a video file across at least two separate machines, and then playing the HLS manifest output to show that the encoding process was successful. This video will be more effective than a live demonstration, as we can trim the excess time waiting for the encode process to complete.

### Work for Today

I created the GitHub repository for the project and started on the overall architecture of the repository, creating folders and template READMEs for each of the three components as well as a number of documents in the docs folder to contain system-level documentation. I also wrote a draft proto file, which sets up a lot of the data modeling of the project, and wrote parts of much of the low-level functional documentation for the components. My focus has been on writing the documentation for the coordinator. The details of the worker (and some of the job specifics in the proto file) are a lot more subject to change, depending on how the logistics of performing a segmented encode end up looking. I'm more comfortable with the distributed systems decisions than the multimedia encoding ones - those I have a rough idea but I might have to figure out more as I go!

### An Inevitable (For Now) Weakness

Splitting a video file before encoding it essentially deprives the video codec of the ability to decide where keyframes should be placed. Keyframes are an important part of the video codec, and bad keyframe placement increases bitrate, even when using a better codec. Since the segmented approach used here can break proper keyframe placement, it may result in some quality or bitrate tradeoffs at the moment. This system is largely a proof of concept, and also is built without tight integration with the underlying video codec - we could switch AV1 for any other codec without too many changes. A first pass keyframing step would improve the performance and utility of a system like this, but is impractical for us to implement here. Rigid keyframing like this, however, is common already when generating HLS encodes, or even just streamable video encodes more generally, and thus is at least not a weakness specific to this approach.

## April 14, 2025

I've been taking a break from this project recently as I have been busy with other schoolwork - I'm returning to it now! I've completed an early draft of the documentation, and realized that I had missed a necessary field in one of the protobuf messages while doing so (an output directory for generated HLS manifests) - this has now been corrected! I wouldn't be surprised if I run into more similar issues as I continue.

Today I'm planning to get somewhat of a start on the client. I'm going to write it in Python, to match with the work Catherine has been doing. As I'm not an expert on how to build CLIs in Python, this might take some research! I'll also have to figure out how to build test handling and a mock server, but can likely borrow some of this from what Catherine has already written.

I've figured out how to generate the compiled proto files:

```
python -m grpc_tools.protoc -I./proto --python_out=client/proto --grpc_python_out=client/proto proto/avspl1t.proto
```

(from the root directory). I know Catherine's done this a lot before, but it's my first time using Python rather than Java for gRPC/Protobuf!

With a bit of work, I've finished a simple client. I used a CLI library to make building this a little easier and more user friendly. It's very simple right now - only around 100 lines of code - but it can generate job details and submit them to the server! No S3 support yet, as I'm putting that off until everything works with local files - it should slide cleanly on top of the existing code. I'll also need to write some tests for the client, which I'm planning to do tomorrow. (Note to myself tomorrow: I think the easiest way to handle the server config for testing is to short-circuit it with an environment variable.)

## April 15, 2025

I've written a set of tests for the client. The client testing approach is perhaps a bit unusual - my "unit tests" here are more like integration tests, which run the client as a separate process as a user would, given that a lot of the logic has to deal with command line input processing and output. In order to do this, my tests run a mock gRPC server and provide an environment variable to the client that leads it to use this server. This mock gRPC server then allows the tests to configure what response it should give to a request and to view the request made to it. Since this requires some multithreading, I've run into some race conditions, which I've resolved by adding small sleep calls to the tests. These race conditions aren't an issue in the actual system, but just in the testing infrastructure I've written to allow a more end-to-end test to be performed. From my knowledge of how gRPC systems are usually tested, this is not exactly the normal approach, but it does allow for more comprehensive testing of the entire system and has some distinct advantages over a black-box fine-grained unit testing approach! In any case, the client and all of the testing needed for its current functionality is done. I'll be working on the S3 components of it later.

Now that this is complete, I can move on to writing the worker. It'll be able to take a bit from the client, as it also needs to interact with the coordinator server. I can take the same testing approach and copy some of the gRPC interaction code, though of course the requests to the server and what is done with them will be completely different. The worker is also not a CLI-based app - it's a continuously running service. Ideally, I'd like to have a substantial amount of the worker done today - the starting components will be the infrastructural ones that don't deal with FFmpeg/video encoding (getting tasks from the coordinator, reporting back results, handling temporary files). This should provide a good base on which to build the components of the worker that will actually implement the logic of each task type!

_Update 1_

I've completed the beginnings of the worker, including methods for all the worker-coordinator communication (and unit tests for these methods) and the filesystem logic, with unfilled methods for S3 and completed methods for FS filesystem methods. Going to move on to trying to draft the actual logic components. I'll hopefully be able to get at least one of these done today! They should all follow somewhat similar patterns, so once I have one fully working and tested, it's just the detail-oriented bits (how to actually work with the video/HLS data) that need to be refined. That's the part I'll need to put the most thought into, so it'll be good to have the rest out of the way.
