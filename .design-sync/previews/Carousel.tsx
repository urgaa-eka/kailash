import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
  Card,
  CardContent,
} from 'frontend';

// CarouselPrevious/Next read the carousel's embla context, so they are composed
// inside <Carousel> here — outside it they throw "useCarousel must be used
// within a <Carousel />".
export const Default = () => (
  <div className="w-[420px] px-12">
    <Carousel>
      <CarouselContent>
        {['Gurugram', 'Cyber City', 'Sohna Road', 'Manesar'].map((zone) => (
          <CarouselItem key={zone}>
            <Card>
              <CardContent className="flex h-32 flex-col items-center justify-center gap-1 p-6">
                <span className="text-lg font-semibold">{zone}</span>
                <span className="text-sm text-muted-foreground">Zone overview</span>
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  </div>
);

export const MultiPerView = () => (
  <div className="w-[440px] px-12">
    <Carousel opts={{ align: 'start' }}>
      <CarouselContent className="-ml-2">
        {['42.6', '18.1', '61.0', '7.4', '33.2'].map((kwh, i) => (
          <CarouselItem key={i} className="basis-1/3 pl-2">
            <Card>
              <CardContent className="flex h-24 flex-col items-center justify-center p-4">
                <span className="text-xl font-semibold">{kwh}</span>
                <span className="text-xs text-muted-foreground">kWh</span>
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  </div>
);
